"""
Intelligence AI Platform - Company Model
Company/Organization management
"""

from sqlalchemy import Column, Integer, String, Text, JSON
#from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Company(Base):
    """Company model for multi-tenant support"""
    __tablename__ = "companies"
    
    # Basic info
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)

    # Industry and size
    industry = Column(String(100))
    size = Column(String(50))  # micro, small, medium, large

    # Contact info
    website = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))

    # Address
    address_street = Column(String(255))
    address_city = Column(String(100))
    address_country = Column(String(100))
    address_postal_code = Column(String(20))

    # Settings and configuration
    settings = Column(JSON, default=dict)

    # Subscription info
    subscription_plan = Column(String(50), default="free")
    subscription_status = Column(String(50), default="active")

    # Relationships
#    tasks = relationship("Task", back_populates="company")
#    tickets = relationship("Ticket", back_populates="company")
#    activities = relationship("Activity", back_populates="company")

    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}')>"

# ✅ Import delayed dependencies to avoid circular imports
import app.models.task
import app.models.ticket
import app.models.activity
