from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.template import Template
from backend.app.models.user import User, TemplateUserAccess, Role
from backend.app.schemas.template import TemplateAssignRequest
from backend.app.routers.auth import get_current_user

router = APIRouter(prefix="/permissions", tags=["Permissions"])

@router.get("/template/{template_id}")
def get_template_permissions(template_id: int, db: Session = Depends(get_db)):
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Get all client users
    client_role = db.query(Role).filter(Role.name == "Client user").first()
    clients = db.query(User).filter(User.role_id == client_role.id).all() if client_role else []

    accesses = db.query(TemplateUserAccess).filter(
        TemplateUserAccess.template_id == template_id,
        TemplateUserAccess.revoked_at == None
    ).all()
    assigned_user_ids = {a.user_id for a in accesses}

    return {
        "template_id": template.id,
        "template_name": template.name,
        "status": template.status,
        "clients": [
            {
                "user_id": c.id,
                "name": c.name,
                "email": c.email,
                "department": c.department,
                "has_access": c.id in assigned_user_ids
            }
            for c in clients
        ]
    }

@router.post("/assign")
def assign_template_access(
    req: TemplateAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    template = db.query(Template).filter(Template.id == req.template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Remove existing active accesses not in the new list
    existing = db.query(TemplateUserAccess).filter(
        TemplateUserAccess.template_id == req.template_id,
        TemplateUserAccess.revoked_at == None
    ).all()

    for acc in existing:
        if acc.user_id not in req.user_ids:
            acc.revoked_at = datetime.utcnow()

    # Add new accesses
    current_user_ids = {a.user_id for a in existing if a.revoked_at is None}
    for u_id in req.user_ids:
        if u_id not in current_user_ids:
            new_acc = TemplateUserAccess(
                template_id=req.template_id,
                user_id=u_id,
                start_date=datetime.utcnow()
            )
            db.add(new_acc)

    db.commit()
    return {"message": f"Permissions updated for template '{template.name}'."}

