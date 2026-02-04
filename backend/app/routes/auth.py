from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Role, UserRole
from app.schemas import UserRegister, UserLogin, UserResponse, UserAuthResponse, ResponseModel, APIKeyResponse
from app.auth import verify_password, get_password_hash, create_access_token, get_current_user
from datetime import datetime
import secrets
import os

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=ResponseModel)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="用户名或邮箱已存在"
        )
    
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    user_role = db.query(Role).filter(Role.name == "user").first()
    if user_role:
        user_role_association = UserRole(user_id=new_user.id, role_id=user_role.id)
        db.add(user_role_association)
        db.commit()
    
    return ResponseModel(
        data={
            "user_id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "created_at": new_user.created_at
        }
    )


@router.post("/login", response_model=ResponseModel)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_data.username).first()
    
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # access_token = create_access_token(data={"sub": user.id})
    access_token = create_access_token(data={"sub": str(user.id)})

    
    return ResponseModel(
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "user_id": user.id,
                "username": user.username,
                "email": user.email
            }
        }
    )
