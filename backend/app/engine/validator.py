import os
import time
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session

from backend.app.models.template import Template, TemplateColumn, Rule, TemplateColumnRule
from backend.app.models.validation import Load, LoadedFile, ValidationError
from backend.app.models.audit import Notification, AuditLog
from backend.app.engine.rule_evaluator import RuleEvaluator
from backend.app.engine.excel_reporter import ExcelReporter
from backend.app.config import settings

class DatasetValidator:
    """
    Core deterministic data validation pipeline for Accura.
    Handles file parsing, schema integrity checks, multi-rule evaluation,
    error logging, traceability, and report generation.
    """

    @classmethod
    def process_and_validate(
        cls,
        db: Session,
        template_id: int,
        user_id: int,
        file_path: str,
        filename: str
    ) -> Dict[str, Any]:
        start_time = time.time()

        # 1. Retrieve template with configured columns and rules
        template = db.query(Template).filter(Template.id == template_id).first()
        if not template:
            raise ValueError(f"Template with id {template_id} not found.")

        # Create Load record in Running status
        load_record = Load(
            template_id=template.id,
            user_id=user_id,
            filename=filename,
            status="Running",
            start_date=datetime.utcnow()
        )
        db.add(load_record)
        db.commit()
        db.refresh(load_record)

        # 2. Parse file into DataFrame
        try:
            if filename.lower().endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path, engine='openpyxl')
            elif filename.lower().endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                raise ValueError("Unsupported file format. Please upload an Excel (.xlsx, .xls) or CSV file.")
        except Exception as e:
            load_record.status = "Failed"
            load_record.finished_at = datetime.utcnow()
            db.commit()
            raise ValueError(f"Failed to read file: {str(e)}")

        # Store loaded file metadata
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        loaded_file = LoadedFile(
            load_id=load_record.id,
            name=filename,
            path=file_path,
            size_bytes=file_size,
            num_rows=len(df),
            created_user_id=user_id
        )
        db.add(loaded_file)
        db.commit()

        # 3. Structural Header Verification (Template compatibility check)
        expected_columns = [col.name.strip() for col in template.columns if col.is_active and not col.deleted]
        actual_columns = [str(col).strip() for col in df.columns]

        missing_required_headers = []
        for col in template.columns:
            if col.is_required and col.name.strip() not in actual_columns:
                missing_required_headers.append(col.name)

        if missing_required_headers:
            # File structure does not match template - reject as per paper Figure 16
            load_record.status = "Rejected"
            load_record.total_rows = len(df)
            load_record.error_rows = len(df)
            load_record.valid_rows = 0
            load_record.validation_time_ms = (time.time() - start_time) * 1000.0
            load_record.finished_at = datetime.utcnow()

            error_obj = ValidationError(
                load_id=load_record.id,
                row_number=1,
                column_name="SCHEMA_HEADERS",
                violated_rule_name="Template Structure Match",
                invalid_value=", ".join(missing_required_headers),
                severity="Error",
                error_message=f"Uploaded file does not match template '{template.name}'. Missing required column headers: {', '.join(missing_required_headers)}"
            )
            db.add(error_obj)

            notif = Notification(
                user_id=user_id,
                event_type="VALIDATION_REJECTED",
                title=f"Validation Failed: {filename}",
                message=f"The uploaded file does not match expected columns for template '{template.name}'."
            )
            db.add(notif)
            db.commit()

            return {
                "load_id": load_record.id,
                "status": "Rejected",
                "total_rows": len(df),
                "valid_rows": 0,
                "error_rows": len(df),
                "validation_time_ms": load_record.validation_time_ms,
                "errors": [{
                    "row_number": 1,
                    "column_name": "SCHEMA_HEADERS",
                    "violated_rule_name": "Template Structure Match",
                    "invalid_value": ", ".join(missing_required_headers),
                    "severity": "Error",
                    "error_message": error_obj.error_message
                }]
            }

        # 4. Map columns to their assigned validation rules
        # Pre-load rules for fast in-memory execution
        column_rules_map: Dict[str, List[Tuple[int, str, Dict[str, Any]]]] = {}
        for col in template.columns:
            if not col.is_active or col.deleted:
                continue
            rules_list = []
            for col_rule in col.column_rules:
                r = col_rule.rule
                if r.is_active and not r.deleted:
                    try:
                        rule_json = json.loads(r.json_rule) if isinstance(r.json_rule, str) else r.json_rule
                        rules_list.append((r.id, r.name, rule_json))
                    except Exception:
                        pass
            column_rules_map[col.name] = rules_list

        # Convert DataFrame to records with row index
        records = df.to_dict(orient="records")
        total_rows = len(records)

        errors_to_db: List[ValidationError] = []
        errors_response: List[Dict[str, Any]] = []
        rows_with_errors = set()
        rule_breakdown: Dict[str, int] = {}

        # 5. Row-by-Row Deterministic Evaluation
        for row_idx, row_data in enumerate(records, start=2):  # start=2 corresponds to Excel line numbers (1 is header)
            # Evaluate all configured columns
            for col_name, rules in column_rules_map.items():
                for rule_id, rule_name, rule_json in rules:
                    res = RuleEvaluator.evaluate(rule_json, row_data, col_name)
                    if not res.is_valid:
                        rows_with_errors.add(row_idx)
                        raw_invalid_val = row_data.get(col_name)
                        str_invalid_val = "" if pd.isna(raw_invalid_val) else str(raw_invalid_val)

                        err_entry = {
                            "row_number": row_idx,
                            "column_name": col_name,
                            "violated_rule_id": rule_id,
                            "violated_rule_name": rule_name,
                            "invalid_value": str_invalid_val,
                            "severity": res.severity,
                            "error_message": res.error_message
                        }
                        errors_response.append(err_entry)

                        errors_to_db.append(ValidationError(
                            load_id=load_record.id,
                            row_number=row_idx,
                            column_name=col_name,
                            violated_rule_id=rule_id,
                            violated_rule_name=rule_name,
                            invalid_value=str_invalid_val,
                            severity=res.severity,
                            error_message=res.error_message
                        ))

                        rule_breakdown[rule_name] = rule_breakdown.get(rule_name, 0) + 1

        error_rows_count = len(rows_with_errors)
        valid_rows_count = total_rows - error_rows_count
        validation_time_ms = (time.time() - start_time) * 1000.0

        # Determine Final Status
        final_status = "Completed" if error_rows_count == 0 else "Rejected"

        # 6. Generate Excel Report
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"DataGuard_Report_{template.name}_{load_record.id}_{timestamp_str}.xlsx"
        report_full_path = os.path.join(settings.REPORT_DIR, report_filename)

        ExcelReporter.generate_report(
            output_path=report_full_path,
            template_name=template.name,
            filename=filename,
            total_rows=total_rows,
            valid_rows=valid_rows_count,
            error_rows=error_rows_count,
            validation_time_ms=validation_time_ms,
            errors=errors_response,
            rule_breakdown=rule_breakdown
        )

        # 7. Persist to Database
        load_record.status = final_status
        load_record.total_rows = total_rows
        load_record.valid_rows = valid_rows_count
        load_record.error_rows = error_rows_count
        load_record.validation_time_ms = validation_time_ms
        load_record.finished_at = datetime.utcnow()
        load_record.report_path = report_full_path

        if errors_to_db:
            db.bulk_save_objects(errors_to_db)

        # Create user notification
        notif_title = f"Validation Passed: {filename}" if final_status == "Completed" else f"Validation Inconsistencies: {filename}"
        notif_msg = (
            f"Dataset processed successfully with 100% compliance ({total_rows} rows)."
            if final_status == "Completed"
            else f"Validation finished with {len(errors_to_db)} inconsistencies detected across {error_rows_count} rows."
        )
        notif = Notification(
            user_id=user_id,
            event_type="VALIDATION_SUCCESS" if final_status == "Completed" else "VALIDATION_REJECTED",
            title=notif_title,
            message=notif_msg,
            payload=json.dumps({"load_id": load_record.id, "errors_count": len(errors_to_db)})
        )
        db.add(notif)

        # Create audit log
        audit = AuditLog(
            template_name=template.name,
            column_name="ALL",
            operation="UPLOAD_VALIDATE",
            details=f"File {filename} validated. Total: {total_rows}, Valid: {valid_rows_count}, Errors: {error_rows_count}",
            created_by=f"User #{user_id}"
        )
        db.add(audit)
        db.commit()

        return {
            "load_id": load_record.id,
            "status": final_status,
            "total_rows": total_rows,
            "valid_rows": valid_rows_count,
            "error_rows": error_rows_count,
            "accuracy_percentage": round((valid_rows_count / max(total_rows, 1)) * 100.0, 2),
            "validation_time_ms": round(validation_time_ms, 2),
            "report_path": report_filename,
            "errors": errors_response[:250],  # Return first 250 for fast API preview
            "total_error_count": len(errors_response)
        }

