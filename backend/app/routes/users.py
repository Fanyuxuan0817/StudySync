from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, APIKey
from app.schemas import UserResponse, ResponseModel, APIKeyResponse
from app.auth import get_current_user, get_password_hash
import secrets
from datetime import datetime, timedelta

router = APIRouter(prefix="/users", tags=["用户"])


@router.get("/me", response_model=ResponseModel)
async def get_me(current_user: User = Depends(get_current_user)):
    return ResponseModel(
        data={
            "user_id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "avatar_url": current_user.avatar_url,
            "created_at": current_user.created_at
        }
    )


@router.post("/api_key", response_model=ResponseModel)
async def create_api_key(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    api_key = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=365)
    
    new_api_key = APIKey(
        key=api_key,
        description=f"API Key for {current_user.username}",
        expires_at=expires_at,
        is_active=True
    )
    db.add(new_api_key)
    db.commit()
    db.refresh(new_api_key)
    
    return ResponseModel(
        data=APIKeyResponse(
            api_key=new_api_key.key,
            created_at=new_api_key.created_at
        ).model_dump()
    )
