from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.api.v1 import auth, user


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events"""
    # Startup: Initialize database
    await init_db()
    yield
    # Shutdown: cleanup if needed
    pass


app = FastAPI(
    title="Loconovo Backend API",
    description="Backend API for Loconovo mobile application",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/v1/auth", tags=["Authentication"])
app.include_router(user.router, prefix="/v1/user", tags=["User"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "loconovo-backend"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Loconovo Backend API",
        "version": "1.0.0",
        "docs": "/docs"
    }

