from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    name: str
    email: str
    role: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

class RoleResponse(BaseModel):
    id: int
    name: str
    status: str

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: str
    password: str

class UserCreate(BaseModel):
    role_id: int
    name: str
    email: str
    password: str
    document: Optional[str] = None
    department: Optional[str] = "InsurTech"
    send_emails: Optional[bool] = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    role_id: Optional[int] = None
    document: Optional[str] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None
    status: Optional[str] = None
    send_emails: Optional[bool] = None

class UserResponse(BaseModel):
    id: int
    role_id: int
    role_name: Optional[str] = None
    document: Optional[str] = None
    name: str
    email: str
    must_change_password: bool
    last_login: Optional[datetime] = None
    department: str
    send_emails: bool
    is_active: bool
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

