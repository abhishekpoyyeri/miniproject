from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class RuleExample(BaseModel):
    valid_example: Optional[Any] = Field(None, alias="Valid example")
    invalid_example: Optional[Any] = Field(None, alias="Invalid example")

    class Config:
        populate_by_name = True

# Standard JSON rule structure defined in Accura Paper (Section III-C)
class AccuraRuleDefinition(BaseModel):
    rule_name: str = Field(..., alias="Rule name")
    data_type: str = Field(..., alias="Data type")
    required_field: bool = Field(False, alias="Required field")
    header: List[str] = Field(..., alias="Header")
    header_rule: Optional[List[str]] = Field(None, alias="Header rule")
    error_message: str = Field(..., alias="Error message")
    description: str = Field(..., alias="Description")
    example: Optional[RuleExample] = Field(None, alias="Example")
    rule: Dict[str, Any] = Field(default_factory=dict, alias="Rule")

    class Config:
        populate_by_name = True

class RuleCreate(BaseModel):
    name: str
    data_type: str
    json_rule: Dict[str, Any]
    prompt_used: Optional[str] = None
    column_id: Optional[int] = None  # If directly assigning to a column

class RuleUpdate(BaseModel):
    name: Optional[str] = None
    data_type: Optional[str] = None
    json_rule: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class RuleResponse(BaseModel):
    id: int
    name: str
    data_type: str
    json_rule: Dict[str, Any]
    effectiveness: float
    prompt_used: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

class RuleGenerateRequest(BaseModel):
    instruction: str
    selected_column: str
    template_headers: List[str]
    suggested_data_type: Optional[str] = None
    template_name: Optional[str] = None

class RuleGenerateResponse(BaseModel):
    success: bool
    generated_rule: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    coherence_passed: bool = True
    retries_used: int = 0

