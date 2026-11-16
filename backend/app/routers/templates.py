import os
import io
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import openpyxl

from backend.app.database import get_db
from backend.app.models.template import Template, TemplateColumn, Rule, TemplateColumnRule
from backend.app.models.user import User, TemplateUserAccess
from backend.app.models.audit import AuditLog
from backend.app.schemas.template import (
    TemplateCreate, TemplateUpdate, TemplateResponse, TemplateDetailResponse,
    ColumnCreate, ColumnResponse
)
from backend.app.schemas.rule import RuleResponse
from backend.app.routers.auth import get_current_user

router = APIRouter(prefix="/templates", tags=["Templates"])

@router.get("", response_model=List[TemplateResponse])
def get_templates(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Template).filter(Template.deleted == False)

    # If client user, only return templates they have permission to see
    if current_user.role and current_user.role.name == "Client user":
        assigned_ids = db.query(TemplateUserAccess.template_id).filter(
            TemplateUserAccess.user_id == current_user.id,
            TemplateUserAccess.revoked_at == None
        ).subquery()
        query = query.filter(Template.id.in_(assigned_ids), Template.status == "Published")
    elif status:
        query = query.filter(Template.status == status)

    templates = query.all()
    results = []
    for t in templates:
        cols = [c for c in t.columns if not c.deleted]
        rule_count = sum(len([cr for cr in c.column_rules if cr.rule and not cr.rule.deleted]) for c in cols)
        results.append(TemplateResponse(
            id=t.id,
            name=t.name,
            table_name=t.table_name,
            description=t.description,
            status=t.status,
            is_active=t.is_active,
            created_by=t.created_by,
            created_at=t.created_at,
            column_count=len(cols),
            rule_count=rule_count
        ))
    return results

@router.get("/{template_id}", response_model=TemplateDetailResponse)
def get_template(template_id: int, db: Session = Depends(get_db)):
    t = db.query(Template).filter(Template.id == template_id, Template.deleted == False).first()
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")

    active_cols = [c for c in t.columns if not c.deleted]
    columns_resp = []
    total_rules = 0

    for c in active_cols:
        col_rules = []
        for cr in c.column_rules:
            r = cr.rule
            if r and not r.deleted:
                try:
                    rule_json = json.loads(r.json_rule) if isinstance(r.json_rule, str) else r.json_rule
                except Exception:
                    rule_json = {}
                col_rules.append(RuleResponse(
                    id=r.id,
                    name=r.name,
                    data_type=r.data_type,
                    json_rule=rule_json,
                    effectiveness=r.effectiveness,
                    prompt_used=r.prompt_used,
                    is_active=r.is_active
                ))
        total_rules += len(col_rules)
        columns_resp.append(ColumnResponse(
            id=c.id,
            template_id=c.template_id,
            name=c.name,
            description=c.description,
            data_type=c.data_type,
            is_required=c.is_required,
            order_index=c.order_index,
            is_active=c.is_active,
            rules=col_rules
        ))

    return TemplateDetailResponse(
        id=t.id,
        name=t.name,
        table_name=t.table_name,
        description=t.description,
        status=t.status,
        is_active=t.is_active,
        created_by=t.created_by,
        created_at=t.created_at,
        column_count=len(active_cols),
        rule_count=total_rules,
        columns=columns_resp
    )

@router.post("", response_model=TemplateDetailResponse)
def create_template(
    temp_in: TemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(Template).filter(Template.name == temp_in.name, Template.deleted == False).first()
    if existing:
        raise HTTPException(status_code=400, detail="A template with this name already exists")

    new_t = Template(
        user_id=current_user.id,
        name=temp_in.name,
        table_name=temp_in.table_name or temp_in.name.lower().replace(" ", "_"),
        description=temp_in.description,
        status="Draft",
        created_by=current_user.name
    )
    db.add(new_t)
    db.commit()
    db.refresh(new_t)

    # Add columns if provided
    if temp_in.columns:
        for idx, col in enumerate(temp_in.columns):
            new_col = TemplateColumn(
                template_id=new_t.id,
                name=col.name,
                description=col.description,
                data_type=col.data_type,
                is_required=col.is_required,
                order_index=idx,
                created_by=current_user.name
            )
            db.add(new_col)
            db.commit()
            db.refresh(new_col)

            # Assign rules
            for r_id in (col.rule_ids or []):
                tcr = TemplateColumnRule(template_column_id=new_col.id, rule_id=r_id)
                db.add(tcr)
        db.commit()

    # Audit log
    audit = AuditLog(
        template_name=new_t.name,
        operation="CREATE_TEMPLATE",
        details=f"Template created with {len(temp_in.columns or [])} columns",
        created_by=current_user.name
    )
    db.add(audit)
    db.commit()

    return get_template(new_t.id, db)

@router.patch("/{template_id}/status")
def update_template_status(
    template_id: int,
    status_update: TemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    t = db.query(Template).filter(Template.id == template_id, Template.deleted == False).first()
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")

    if status_update.status:
        t.status = status_update.status
    if status_update.name:
        t.name = status_update.name
    if status_update.description:
        t.description = status_update.description
    t.updated_by = current_user.name
    db.commit()

    audit = AuditLog(
        template_name=t.name,
        operation="STATUS_CHANGE",
        details=f"Template status changed to {t.status}",
        created_by=current_user.name
    )
    db.add(audit)
    db.commit()

    return {"id": t.id, "status": t.status, "name": t.name}

@router.post("/{template_id}/columns")
def add_column(
    template_id: int,
    col_in: ColumnCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    t = db.query(Template).filter(Template.id == template_id, Template.deleted == False).first()
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")

    order_idx = len(t.columns)
    new_col = TemplateColumn(
        template_id=t.id,
        name=col_in.name,
        description=col_in.description,
        data_type=col_in.data_type,
        is_required=col_in.is_required,
        order_index=order_idx,
        created_by=current_user.name
    )
    db.add(new_col)
    db.commit()
    db.refresh(new_col)

    for r_id in (col_in.rule_ids or []):
        tcr = TemplateColumnRule(template_column_id=new_col.id, rule_id=r_id)
        db.add(tcr)
    db.commit()

    return {"message": "Column added successfully", "column_id": new_col.id}

@router.get("/{template_id}/sample-excel")
def download_sample_excel(template_id: int, db: Session = Depends(get_db)):
    """
    Downloads a blank template Excel file (.xlsx) with pre-filled headers
    so users can populate and test uploads.
    """
    t = db.query(Template).filter(Template.id == template_id, Template.deleted == False).first()
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = t.name[:31]

    columns = [c.name for c in t.columns if not c.deleted]
    ws.append(columns)

    # Style header row
    header_fill = openpyxl.styles.PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    white_font = openpyxl.styles.Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")

    for col_idx in range(1, len(columns) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = white_font
        col_letter = openpyxl.utils.get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = max(len(columns[col_idx-1]) + 5, 15)

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    filename = f"{t.name}_template.xlsx"
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

