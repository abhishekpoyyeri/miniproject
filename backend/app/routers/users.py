from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from backend.app.database import get_db
from backend.app.models.user import User, Role
from backend.app.schemas.user import UserCreate, UserUpdate, UserResponse, RoleResponse
from backend.app.routers.auth import hash_password, get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/roles", response_model=List[RoleResponse])
def get_roles(db: Session = Depends(get_db)):
    return db.query(Role).all()

@router.get("", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    users = db.query(User).all()
    results = []
    for u in users:
        results.append(UserResponse(
            id=u.id,
            role_id=u.role_id,
            role_name=u.role.name if u.role else None,
            document=u.document,
            name=u.name,
            email=u.email,
            must_change_password=u.must_change_password,
            last_login=u.last_login,
            department=u.department or "InsurTech",
            send_emails=u.send_emails,
            is_active=u.is_active,
            status=u.status,
            created_at=u.created_at
        ))
    return results

@router.post("", response_model=UserResponse)
def create_user(user_in: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    new_user = User(
        role_id=user_in.role_id,
        name=user_in.name,
        email=user_in.email,
        password=hash_password(user_in.password),
        document=user_in.document,
        department=user_in.department,
        send_emails=user_in.send_emails if user_in.send_emails is not None else True,
        is_active=True,
        status="Active",
        created_by=current_user.name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse(
        id=new_user.id,
        role_id=new_user.role_id,
        role_name=new_user.role.name if new_user.role else None,
        document=new_user.document,
        name=new_user.name,
        email=new_user.email,
        must_change_password=new_user.must_change_password,
        last_login=new_user.last_login,
        department=new_user.department or "InsurTech",
        send_emails=new_user.send_emails,
        is_active=new_user.is_active,
        status=new_user.status,
        created_at=new_user.created_at
    )

@router.patch("/{user_id}/status")
def toggle_user_status(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = not user.is_active
    user.status = "Active" if user.is_active else "Inactive"
    db.commit()
    return {"id": user.id, "is_active": user.is_active, "status": user.status}

