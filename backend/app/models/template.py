from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Template(Base):
    __tablename__ = "template"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    name = Column(String(100), unique=True, nullable=False)
    table_name = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="Draft")  # Draft, Published, Archived
    is_active = Column(Boolean, default=True)
    deleted = Column(Boolean, default=False)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(String(100), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_by = Column(String(100), nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    columns = relationship("TemplateColumn", back_populates="template", cascade="all, delete-orphan", order_by="TemplateColumn.order_index")
    user_accesses = relationship("TemplateUserAccess", back_populates="template", cascade="all, delete-orphan")
    loads = relationship("Load", back_populates="template")

class TemplateColumn(Base):
    __tablename__ = "template_column"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("template.id"), nullable=False)
    name = Column(String(100), nullable=False)  # Column header name in file
    description = Column(Text, nullable=True)
    data_type = Column(String(50), nullable=False)  # Text, Number, Date, List, etc.
    is_required = Column(Boolean, default=False)
    order_index = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    deleted = Column(Boolean, default=False)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(String(100), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_by = Column(String(100), nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    template = relationship("Template", back_populates="columns")
    column_rules = relationship("TemplateColumnRule", back_populates="column", cascade="all, delete-orphan")

class Rule(Base):
    __tablename__ = "rule"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    data_type = Column(String(50), nullable=False)  # Text, Number, Document, List, Complex List, Phone, Email, Date, Dependency
    json_rule = Column(Text, nullable=False)  # Full JSON schema string according to Section III-C
    effectiveness = Column(Float, default=100.0)
    prompt_used = Column(Text, nullable=True)  # Natural language instruction used with GPT-4o
    is_active = Column(Boolean, default=True)
    deleted = Column(Boolean, default=False)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(String(100), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_by = Column(String(100), nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    column_rules = relationship("TemplateColumnRule", back_populates="rule")

class TemplateColumnRule(Base):
    __tablename__ = "template_column_rule"

    id = Column(Integer, primary_key=True, index=True)
    template_column_id = Column(Integer, ForeignKey("template_column.id"), nullable=False)
    rule_id = Column(Integer, ForeignKey("rule.id"), nullable=False)

    column = relationship("TemplateColumn", back_populates="column_rules")
    rule = relationship("Rule", back_populates="column_rules")

