from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class User(BaseModel):
    id: int
    phone_number: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    phone_number: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

