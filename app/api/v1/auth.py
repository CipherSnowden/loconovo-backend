from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
    get_current_user
)
from app.core.otp import otp_storage
from app.schemas.auth import (
    OTPRequest,
    OTPVerify,
    TokenResponse,
    TokenRefresh,
    MessageResponse
)
from app.schemas.user import UserResponse
from app.models.user import User

router = APIRouter()


@router.post("/send-otp", response_model=MessageResponse)
async def send_otp(
    request: OTPRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Send OTP to phone number.
    For development: OTP will be returned in response. In production, integrate with SMS provider.
    """
    try:
        # Generate and store OTP
        otp_code = otp_storage.send_otp(request.phone_number)
        
        # Log OTP for development (remove in production)
        print(f"[DEV] OTP for {request.phone_number}: {otp_code}")
        
        return MessageResponse(
            message=f"OTP sent successfully. [DEV MODE] OTP: {otp_code}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(
    request: OTPVerify,
    db: AsyncSession = Depends(get_db)
):
    """Verify OTP and return JWT tokens"""
    # Verify OTP
    if not otp_storage.verify_otp(request.phone_number, request.otp_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
    
    # Check if user exists, if not create new user
    result = await db.execute(
        select(User).where(User.phone_number == request.phone_number)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        # Create new user
        user = User(phone_number=request.phone_number, is_active=True)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.id, "phone": user.phone_number})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: TokenRefresh,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token"""
    # Verify refresh token
    payload = verify_token(request.refresh_token, is_refresh=True)
    user_id: int = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Verify user exists and is active
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Generate new access token
    access_token = create_access_token(data={"sub": user.id, "phone": user.phone_number})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=request.refresh_token,  # Refresh token remains the same
        token_type="bearer"
    )


@router.post("/logout", response_model=MessageResponse)
async def logout():
    """
    Logout endpoint.
    Client should remove tokens from storage.
    In future, can implement token blacklisting here.
    """
    return MessageResponse(message="Logged out successfully")


@router.get("/me", response_model=UserResponse)
async def get_me(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """Get current authenticated user information"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
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

