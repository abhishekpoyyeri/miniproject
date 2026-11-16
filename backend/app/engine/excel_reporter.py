import os
from datetime import datetime
from typing import List, Dict, Any
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

class ExcelReporter:
    """
    Generates styled enterprise validation reports in Excel format (.xlsx)
    with a KPI Executive Summary sheet and a granular Structural Inconsistencies sheet.
    """

    @classmethod
    def generate_report(
        cls,
        output_path: str,
        template_name: str,
        filename: str,
        total_rows: int,
        valid_rows: int,
        error_rows: int,
        validation_time_ms: float,
        errors: List[Dict[str, Any]],
        rule_breakdown: Dict[str, int] = None
    ) -> str:
        wb = openpyxl.Workbook()

        # Styles
        primary_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")  # Dark Blue
        header_fill = PatternFill(start_color="2563EB", end_color="2563EB", fill_type="solid")   # Blue
        accent_fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")   # Light gray
        error_cell_fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid") # Soft Red
        success_fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")  # Soft Green

        white_bold = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
        title_font = Font(name="Segoe UI", size=16, bold=True, color="1E3A8A")
        sub_font = Font(name="Segoe UI", size=11, color="475569")
        bold_font = Font(name="Segoe UI", size=11, bold=True, color="1E293B")
        regular_font = Font(name="Segoe UI", size=10, color="0F172A")
        error_font = Font(name="Segoe UI", size=10, color="991B1B", bold=True)

        thin_border = Border(
            left=Side(style='thin', color="CBD5E1"),
            right=Side(style='thin', color="CBD5E1"),
            top=Side(style='thin', color="CBD5E1"),
            bottom=Side(style='thin', color="CBD5E1")
        )

        # ----------------------------------------------------------------------
        # SHEET 1: Summary Sheet
        # ----------------------------------------------------------------------
        ws_sum = wb.active
        ws_sum.title = "Validation Summary"
        ws_sum.views.sheetView[0].showGridLines = True

        # Header Title
        ws_sum.merge_cells("B2:F2")
        ws_sum["B2"] = "DATAGUARD AI — DATA MIGRATION VALIDATION REPORT"
        ws_sum["B2"].font = title_font
        ws_sum["B2"].alignment = Alignment(vertical="center")

        ws_sum.merge_cells("B3:F3")
        ws_sum["B3"] = f"InsurTech Quality Assurance | Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ws_sum["B3"].font = sub_font

        # Overview Table
        summary_rows = [
            ("Migration Template", template_name),
            ("Source Dataset File", filename),
            ("Execution Status", "COMPLETED (NO INCONSISTENCIES)" if error_rows == 0 else "REJECTED (INCONSISTENCIES DETECTED)"),
            ("Total Records Evaluated", total_rows),
            ("Valid Records (Passed)", valid_rows),
            ("Erroneous Records", error_rows),
            ("Data Accuracy Rate (%)", f"{(valid_rows / max(total_rows, 1) * 100):.2f}%"),
            ("Validation Execution Time", f"{(validation_time_ms / 1000.0):.2f} seconds"),
            ("Total Detected Inconsistencies", len(errors))
        ]

        start_r = 5
        ws_sum.cell(row=start_r, column=2, value="Execution Parameter").font = white_bold
        ws_sum.cell(row=start_r, column=2).fill = primary_fill
        ws_sum.cell(row=start_r, column=2).alignment = Alignment(horizontal="left")

        ws_sum.cell(row=start_r, column=3, value="Validation Result").font = white_bold
        ws_sum.cell(row=start_r, column=3).fill = primary_fill
        ws_sum.cell(row=start_r, column=3).alignment = Alignment(horizontal="left")

        for idx, (label, val) in enumerate(summary_rows, start=start_r + 1):
            c_lbl = ws_sum.cell(row=idx, column=2, value=label)
            c_lbl.font = bold_font
            c_lbl.border = thin_border
            c_lbl.fill = accent_fill

            c_val = ws_sum.cell(row=idx, column=3, value=val)
            c_val.font = regular_font
            c_val.border = thin_border
            if label == "Execution Status":
                c_val.fill = success_fill if error_rows == 0 else error_cell_fill
                c_val.font = bold_font

        # Rule Breakdown Table
        if rule_breakdown and len(rule_breakdown) > 0:
            brk_start = len(summary_rows) + start_r + 2
            ws_sum.cell(row=brk_start, column=2, value="Violated Rule Name").font = white_bold
            ws_sum.cell(row=brk_start, column=2).fill = header_fill
            ws_sum.cell(row=brk_start, column=3, value="Violation Count").font = white_bold
            ws_sum.cell(row=brk_start, column=3).fill = header_fill

            for r_idx, (r_name, r_count) in enumerate(rule_breakdown.items(), start=brk_start + 1):
                c1 = ws_sum.cell(row=r_idx, column=2, value=r_name)
                c1.font = regular_font
                c1.border = thin_border
                c2 = ws_sum.cell(row=r_idx, column=3, value=r_count)
                c2.font = bold_font
                c2.border = thin_border
                c2.alignment = Alignment(horizontal="right")

        # ----------------------------------------------------------------------
        # SHEET 2: Inconsistencies Log
        # ----------------------------------------------------------------------
        ws_err = wb.create_sheet(title="Structural Inconsistencies")
        ws_err.views.sheetView[0].showGridLines = True

        headers = ["#", "Row Number", "Column / Header", "Violated Rule", "Invalid Value", "Severity", "Observation / Description"]
        ws_err.append([])  # empty top row
        ws_err.append(["", "LIST OF DETECTED STRUCTURAL INCONSISTENCIES"])
        ws_err["B2"].font = title_font

        header_row_idx = 4
        for col_idx, h_text in enumerate(headers, start=2):
            cell = ws_err.cell(row=header_row_idx, column=col_idx, value=h_text)
            cell.font = white_bold
            cell.fill = primary_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border

        if not errors:
            ws_err.cell(row=5, column=2, value="No structural inconsistencies detected in this dataset.").font = bold_font
            ws_err.cell(row=5, column=2).fill = success_fill
        else:
            for i, err in enumerate(errors, start=1):
                r_num = header_row_idx + i
                vals = [
                    i,
                    err.get("row_number", "-"),
                    err.get("column_name", "-"),
                    err.get("violated_rule_name", "-"),
                    str(err.get("invalid_value", "")),
                    err.get("severity", "Error"),
                    err.get("error_message", "-")
                ]
                for c_idx, val in enumerate(vals, start=2):
                    cell = ws_err.cell(row=r_num, column=c_idx, value=val)
                    cell.font = regular_font
                    cell.border = thin_border
                    if c_idx == 3:  # Row number
                        cell.alignment = Alignment(horizontal="center")
                    elif c_idx == 6:  # Invalid value
                        cell.fill = error_cell_fill
                    elif c_idx == 7:  # Severity
                        cell.font = error_font
                        cell.alignment = Alignment(horizontal="center")

        # Auto-adjust column widths
        for ws in [ws_sum, ws_err]:
            for col in ws.columns:
                max_len = 0
                col_letter = get_column_letter(col[0].column)
                for cell in col:
                    if cell.value:
                        max_len = max(max_len, len(str(cell.value)))
                ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 65)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        wb.save(output_path)
        return output_path

