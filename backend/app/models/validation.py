from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Load(Base):
    __tablename__ = "load"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("template.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    status = Column(String(50), default="Running")  # Running, Completed (Valid), Rejected (Errors)
    total_rows = Column(Integer, default=0)
    valid_rows = Column(Integer, default=0)
    error_rows = Column(Integer, default=0)
    validation_time_ms = Column(Float, default=0.0)
    report_path = Column(String(255), nullable=True)
    start_date = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    template = relationship("Template", back_populates="loads")
    user = relationship("User", back_populates="loads")
    files = relationship("LoadedFile", back_populates="load", cascade="all, delete-orphan")
    errors = relationship("ValidationError", back_populates="load", cascade="all, delete-orphan")

class LoadedFile(Base):
    __tablename__ = "loaded_file"

    id = Column(Integer, primary_key=True, index=True)
    load_id = Column(Integer, ForeignKey("load.id"), nullable=False)
    name = Column(String(255), nullable=False)
    path = Column(String(255), nullable=False)
    size_bytes = Column(Integer, default=0)
    num_rows = Column(Integer, default=0)
    created_user_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    load = relationship("Load", back_populates="files")

class ValidationError(Base):
    __tablename__ = "validation_error"

    id = Column(Integer, primary_key=True, index=True)
    load_id = Column(Integer, ForeignKey("load.id"), nullable=False)
    row_number = Column(Integer, nullable=False)  # Row in Excel/CSV
    column_name = Column(String(100), nullable=False)  # Violated Column
    violated_rule_id = Column(Integer, nullable=True)
    violated_rule_name = Column(String(150), nullable=False)
    invalid_value = Column(Text, nullable=True)
    severity = Column(String(20), default="Error")  # Error, Warning
    error_message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    load = relationship("Load", back_populates="errors")

