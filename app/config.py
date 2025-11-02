from pydantic_settings import BaseSettings
from typing import List
from pydantic import computed_field
import os
from dotenv import load_dotenv

# Load .env.prod by default, can override with ENV_FILE environment variable
env_file = os.getenv("ENV_FILE", ".env.prod")
load_dotenv(env_file)


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/loconovo_db"
    
    # JWT
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_REFRESH_SECRET_KEY: str = "your-refresh-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # OTP
    OTP_LENGTH: int = 4
    OTP_EXPIRE_MINUTES: int = 5
    OTP_RATE_LIMIT_REQUESTS: int = 5  # Max OTP requests per hour
    
    # CORS - stored as comma-separated string in env file
    # Use alias to map CORS_ORIGINS env var to CORS_ORIGINS_STR field
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8080"
    
    @computed_field
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert comma-separated CORS origins string to list"""
        if not self.CORS_ORIGINS:
            return ["http://localhost:3000", "http://localhost:8080"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    class Config:
        env_file = ".env.prod"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from env file


settings = Settings()

