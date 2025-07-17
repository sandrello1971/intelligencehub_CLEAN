"""
Intelligence AI Platform - Response Schemas
"""

from pydantic import BaseModel
from typing import Any, Optional, List

class APIResponse(BaseModel):
    """Standard API response schema"""
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[Any] = None

class ErrorResponse(BaseModel):
    """Error response schema"""
    success: bool = False
    error: str
    details: Optional[str] = None

class PaginatedResponse(BaseModel):
    """Paginated response schema"""
    success: bool = True
    data: List[Any]
    pagination: dict
    total: int
