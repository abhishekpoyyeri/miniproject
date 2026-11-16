from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from backend.app.schemas.rule import RuleResponse

class ColumnBase(BaseModel):
    name: str
    description: Optional[str] = None
    data_type: str
    is_required: bool = False
    order_index: int = 0

class ColumnCreate(ColumnBase):
    rule_ids: Optional[List[int]] = []

class ColumnResponse(ColumnBase):
    id: int
    template_id: int
    is_active: bool
    rules: List[RuleResponse] = []

    class Config:
        from_attributes = True

class TemplateBase(BaseModel):
    name: str
    table_name: Optional[str] = None
    description: Optional[str] = None

class TemplateCreate(TemplateBase):
    columns: Optional[List[ColumnCreate]] = []

class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None  # Draft, Published, Archived
    is_active: Optional[bool] = None

class TemplateResponse(TemplateBase):
    id: int
    status: str
    is_active: bool
    created_by: Optional[str] = None
    created_at: datetime
    column_count: int = 0
    rule_count: int = 0

    class Config:
        from_attributes = True

class TemplateDetailResponse(TemplateResponse):
    columns: List[ColumnResponse] = []

class TemplateAssignRequest(BaseModel):
    template_id: int
    user_ids: List[int]

