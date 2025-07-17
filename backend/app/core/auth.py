# app/core/auth.py
# Authentication utilities - IntelligenceHUB

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.database import get_db

security = HTTPBearer()

async def get_current_user(token: str = Depends(security), db: Session = Depends(get_db)):
    """
    Get current authenticated user
    TODO: Implement JWT token validation
    """
    # Stub implementation - replace with actual JWT validation
    class MockUser:
        id = "mock-user-id"
        email = "admin@intelligencehub.com"
        is_active = True
    
    return MockUser()
