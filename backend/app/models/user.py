from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Role(Base):
    __tablename__ = "role"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # Administrator, Technical user, Client user
    status = Column(String(20), default="Active")

    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("role.id"), nullable=False)
    document = Column(String(20), nullable=True)
    name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    must_change_password = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    department = Column(String(100), default="InsurTech")
    send_emails = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    status = Column(String(20), default="Active")
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(String(100), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    role = relationship("Role", back_populates="users")
    template_access = relationship("TemplateUserAccess", back_populates="user", cascade="all, delete-orphan")
    loads = relationship("Load", back_populates="user")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

class TemplateUserAccess(Base):
    __tablename__ = "template_user_access"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("template.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="template_access")
    template = relationship("Template", back_populates="user_accesses")

