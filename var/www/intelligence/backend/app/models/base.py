"""
Intelligence AI Platform - Base Model
Base class for all database models with common fields
"""

from sqlalchemy import Column, Integer, DateTime, String, Boolean
from sqlalchemy.sql import func
from app.core.database import Base

class TimestampMixin:
    """Mixin for timestamp fields"""
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

class BaseModel(Base, TimestampMixin):
    """Base model with common fields"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
