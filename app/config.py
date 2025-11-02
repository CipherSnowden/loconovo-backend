from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

# Load .env.prod by default, can override with ENV_FILE environment variable
env_file = os.getenv("ENV_FILE", ".env.prod")
load_dotenv(env_file)


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/loconovo_db"
    )
    
    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_REFRESH_SECRET_KEY: str = os.getenv("JWT_REFRESH_SECRET_KEY", "your-refresh-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # OTP
    OTP_LENGTH: int = 4
    OTP_EXPIRE_MINUTES: int = 5
    OTP_RATE_LIMIT_REQUESTS: int = 5  # Max OTP requests per hour
    
    # CORS
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:8080"
    ).split(",")
    
    class Config:
        env_file = ".env.prod"
        case_sensitive = True


settings = Settings()

