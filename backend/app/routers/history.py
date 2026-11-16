from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.validation import Load, ValidationError
from backend.app.models.user import User
from backend.app.schemas.validation import LoadResponse, LoadDetailResponse, ValidationErrorResponse
from backend.app.routers.auth import get_current_user

router = APIRouter(prefix="/history", tags=["Upload History"])

@router.get("", response_model=List[LoadResponse])
def get_upload_history(
    template_id: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Load)

    # Filter for client user to see their own loads or accessible templates
    if current_user.role and current_user.role.name == "Client user":
        query = query.filter(Load.user_id == current_user.id)

    if template_id:
        query = query.filter(Load.template_id == template_id)
    if status:
        query = query.filter(Load.status == status)

    loads = query.order_by(Load.id.desc()).limit(limit).all()

    results = []
    for l in loads:
        total = l.total_rows or 0
        valid = l.valid_rows or 0
        acc_pct = round((valid / max(total, 1)) * 100.0, 2)
        results.append(LoadResponse(
            id=l.id,
            template_id=l.template_id,
            template_name=l.template.name if l.template else None,
            user_id=l.user_id,
            user_name=l.user.name if l.user else None,
            filename=l.filename,
            status=l.status,
            total_rows=total,
            valid_rows=valid,
            error_rows=l.error_rows or 0,
            accuracy_percentage=acc_pct,
            validation_time_ms=l.validation_time_ms or 0.0,
            start_date=l.start_date,
            finished_at=l.finished_at,
            report_path=l.report_path
        ))
    return results

@router.get("/{load_id}", response_model=LoadDetailResponse)
def get_load_detail(
    load_id: int,
    column: Optional[str] = None,
    rule_name: Optional[str] = None,
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    load = db.query(Load).filter(Load.id == load_id).first()
    if not load:
        raise HTTPException(status_code=404, detail="Validation execution not found")

    err_query = db.query(ValidationError).filter(ValidationError.load_id == load_id)
    if column:
        err_query = err_query.filter(ValidationError.column_name == column)
    if rule_name:
        err_query = err_query.filter(ValidationError.violated_rule_name == rule_name)

    errors = err_query.limit(limit).all()

    total = load.total_rows or 0
    valid = load.valid_rows or 0
    acc_pct = round((valid / max(total, 1)) * 100.0, 2)

    return LoadDetailResponse(
        id=load.id,
        template_id=load.template_id,
        template_name=load.template.name if load.template else None,
        user_id=load.user_id,
        user_name=load.user.name if load.user else None,
        filename=load.filename,
        status=load.status,
        total_rows=total,
        valid_rows=valid,
        error_rows=load.error_rows or 0,
        accuracy_percentage=acc_pct,
        validation_time_ms=load.validation_time_ms or 0.0,
        start_date=load.start_date,
        finished_at=load.finished_at,
        report_path=load.report_path,
        errors=[
            ValidationErrorResponse(
                id=e.id,
                row_number=e.row_number,
                column_name=e.column_name,
                violated_rule_id=e.violated_rule_id,
                violated_rule_name=e.violated_rule_name,
                invalid_value=e.invalid_value,
                severity=e.severity,
                error_message=e.error_message
            )
            for e in errors
        ]
    )

