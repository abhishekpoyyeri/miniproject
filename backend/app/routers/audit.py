from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.audit import Notification, AuditLog
from backend.app.models.user import User
from backend.app.routers.auth import get_current_user

router = APIRouter(prefix="/audit", tags=["Audit & Notifications"])

@router.get("/notifications")
def get_user_notifications(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notifs = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.id.desc()).limit(limit).all()

    return [
        {
            "id": n.id,
            "event_type": n.event_type,
            "title": n.title,
            "message": n.message,
            "read": n.read_at is not None,
            "created_at": n.created_at
        }
        for n in notifs
    ]

@router.post("/notifications/{notif_id}/read")
def mark_notification_read(notif_id: int, db: Session = Depends(get_db)):
    n = db.query(Notification).filter(Notification.id == notif_id).first()
    if n and not n.read_at:
        n.read_at = datetime.utcnow()
        db.commit()
    return {"status": "ok"}

@router.get("/logs")
def get_audit_logs(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logs = db.query(AuditLog).order_by(AuditLog.id.desc()).limit(limit).all()
    return [
        {
            "id": l.id,
            "template_name": l.template_name,
            "column_name": l.column_name,
            "operation": l.operation,
            "details": l.details,
            "created_by": l.created_by,
            "created_at": l.created_at
        }
        for l in logs
    ]

