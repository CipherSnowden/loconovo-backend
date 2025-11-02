import random
from datetime import datetime, timedelta
from typing import Dict, Optional
from collections import defaultdict
from app.config import settings


class OTPStorage:
    """In-memory OTP storage with rate limiting"""
    
    def __init__(self):
        # Structure: {phone_number: {code: str, expires_at: datetime, attempts: int}}
        self._otps: Dict[str, dict] = {}
        # Structure: {phone_number: [request_times]}
        self._rate_limits: Dict[str, list] = defaultdict(list)
    
    def generate_otp(self) -> str:
        """Generate a random 4-digit OTP"""
        return str(random.randint(1000, 9999)).zfill(settings.OTP_LENGTH)
    
    def send_otp(self, phone_number: str) -> str:
        """Generate and store OTP for phone number with rate limiting"""
        # Check rate limit
        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)
        
        # Clean old rate limit entries
        self._rate_limits[phone_number] = [
            req_time for req_time in self._rate_limits[phone_number]
            if req_time > one_hour_ago
        ]
        
        # Check if rate limit exceeded
        if len(self._rate_limits[phone_number]) >= settings.OTP_RATE_LIMIT_REQUESTS:
            raise ValueError(
                f"Rate limit exceeded. Maximum {settings.OTP_RATE_LIMIT_REQUESTS} "
                f"OTP requests per hour allowed."
            )
        
        # Generate and store OTP
        otp_code = self.generate_otp()
        expires_at = now + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
        
        self._otps[phone_number] = {
            "code": otp_code,
            "expires_at": expires_at,
            "attempts": 0
        }
        
        # Record this request for rate limiting
        self._rate_limits[phone_number].append(now)
        
        return otp_code
    
    def verify_otp(self, phone_number: str, otp_code: str) -> bool:
        """Verify OTP code for phone number"""
        if phone_number not in self._otps:
            return False
        
        otp_data = self._otps[phone_number]
        
        # Check if expired
        if datetime.utcnow() > otp_data["expires_at"]:
            del self._otps[phone_number]
            return False
        
        # Check if attempts exceeded (max 5 attempts per OTP)
        if otp_data["attempts"] >= 5:
            del self._otps[phone_number]
            return False
        
        # Increment attempts
        otp_data["attempts"] += 1
        
        # Verify code
        if otp_data["code"] != otp_code:
            return False
        
        # OTP verified successfully - remove it
        del self._otps[phone_number]
        return True
    
    def cleanup_expired(self):
        """Remove expired OTPs (cleanup method)"""
        now = datetime.utcnow()
        expired_numbers = [
            phone for phone, data in self._otps.items()
            if now > data["expires_at"]
        ]
        for phone in expired_numbers:
            del self._otps[phone]


# Global OTP storage instance
otp_storage = OTPStorage()

