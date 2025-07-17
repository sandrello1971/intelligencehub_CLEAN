"""
CRM Links model for external integrations
"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey
#from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class CrmLink(Base):
    __tablename__ = "crm_links"
    
    id = Column(Integer, primary_key=True, index=True)
    local_ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=True)
    crm_activity_id = Column(Integer, nullable=True)
    crm_company_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
#    ticket = relationship("Ticket", back_populates="crm_links")
