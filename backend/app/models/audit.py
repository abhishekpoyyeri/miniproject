from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Notification(Base):
    __tablename__ = "notification"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    event_type = Column(String(50), nullable=False)  # VALIDATION_SUCCESS, VALIDATION_REJECTED, TEMPLATE_ASSIGNED, SYSTEM
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    payload = Column(Text, nullable=True)  # JSON metadata
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")

class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    template_name = Column(String(100), nullable=True)
    column_name = Column(String(100), nullable=True)
    operation = Column(String(100), nullable=False)  # CREATE_RULE, ASSIGN_RULE, UPLOAD_VALIDATE, PUBLISH_TEMPLATE
    details = Column(Text, nullable=True)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(String(100), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

