from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from fastapi import Header, HTTPException

from app.database import get_db
from app.core.security import get_current_user
from app.schemas.user import UserResponse
from app.models.user import User

router = APIRouter()


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """Get user profile (same as /me endpoint, kept for future extensibility)"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing or invalid"
        )
    
    token = authorization.split(" ")[1]
    user = await get_current_user(token, db)
    
    return UserResponse(
        id=user.id,
        phone_number=user.phone_number,
        created_at=user.created_at,
        updated_at=user.updated_at,
        is_active=user.is_active
    )

