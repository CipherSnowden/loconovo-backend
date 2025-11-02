from pydantic import BaseModel, Field, field_validator
import re


class OTPRequest(BaseModel):
    phone_number: str = Field(..., min_length=10, max_length=15, description="Phone number in E.164 format")
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v):
        # Basic phone validation - remove any non-digit characters and validate length
        digits = re.sub(r'\D', '', v)
        if len(digits) < 10 or len(digits) > 15:
            raise ValueError('Phone number must be between 10 and 15 digits')
        return digits


class OTPVerify(BaseModel):
    phone_number: str = Field(..., min_length=10, max_length=15, description="Phone number in E.164 format")
    otp_code: str = Field(..., min_length=4, max_length=4, description="4-digit OTP code")
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v):
        digits = re.sub(r'\D', '', v)
        if len(digits) < 10 or len(digits) > 15:
            raise ValueError('Phone number must be between 10 and 15 digits')
        return digits
    
    @field_validator('otp_code')
    @classmethod
    def validate_otp(cls, v):
        if not v.isdigit():
            raise ValueError('OTP code must contain only digits')
        return v


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


class MessageResponse(BaseModel):
    message: str

