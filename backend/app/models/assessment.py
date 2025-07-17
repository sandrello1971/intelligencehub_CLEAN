"""
Assessment models for business evaluation
"""
from sqlalchemy import Column, String, Integer, Text, JSON, DateTime, Boolean, ForeignKey
#from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class AssessmentSession(Base):
    __tablename__ = "assessment_session"
    
    id = Column(String, primary_key=True)  # UUID
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    azienda_nome = Column(Text, nullable=False)
    settore = Column(Text, nullable=True)
    dimensione = Column(Text, nullable=True)
    referente = Column(Text, nullable=True)
    email = Column(Text, nullable=True)
    risposte_json = Column(JSON, nullable=True)
    punteggi_json = Column(JSON, nullable=True)
    raccomandazioni = Column(Text, nullable=True)
    creato_il = Column(DateTime, default=func.now())
    user_id = Column(String, nullable=True)
    
    # Relationships
#    company = relationship("Company", back_populates="assessment_sessions")
#    results = relationship("AssessmentResult", back_populates="session")

class AssessmentResult(Base):
    __tablename__ = "assessment_result"
    
    id = Column(String, primary_key=True)  # UUID
    session_id = Column(String, ForeignKey("assessment_session.id"), nullable=False)
    process = Column(String(255), nullable=False)
    category = Column(String(255), nullable=False)
    dimension = Column(Text, nullable=False)
    score = Column(Integer, nullable=False)  # 1-5 scale
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_not_applicable = Column(Boolean, default=False)
    
    # Relationships
#    session = relationship("AssessmentSession", back_populates="results")
