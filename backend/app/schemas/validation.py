from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class ValidationErrorResponse(BaseModel):
    id: int
    row_number: int
    column_name: str
    violated_rule_id: Optional[int] = None
    violated_rule_name: str
    invalid_value: Optional[str] = None
    severity: str
    error_message: str

    class Config:
        from_attributes = True

class LoadResponse(BaseModel):
    id: int
    template_id: int
    template_name: Optional[str] = None
    user_id: int
    user_name: Optional[str] = None
    filename: str
    status: str
    total_rows: int
    valid_rows: int
    error_rows: int
    accuracy_percentage: float = 0.0
    validation_time_ms: float
    start_date: datetime
    finished_at: Optional[datetime] = None
    report_path: Optional[str] = None

    class Config:
        from_attributes = True

class LoadDetailResponse(LoadResponse):
    errors: List[ValidationErrorResponse] = []

class BenchmarkMetrics(BaseModel):
    scenario: str
    acc: float  # Rule definition accuracy %
    adr: float  # Rule adjustment rate %
    validation_time_min: float  # Average minutes per template
    format_val_time_min: float
    rule_creation_time_min: float
    rule_verification_time_min: float
    data_val_time_min: float
    precision: float  # %
    recall: float  # %
    f1_score: float  # %
    tp: int
    fp: int
    fn: int

