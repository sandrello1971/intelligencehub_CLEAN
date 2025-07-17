"""
Contacts model for business cards and CRM
"""
from sqlalchemy import Column, String, Text, JSON, DateTime, ForeignKey
#from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(String, primary_key=True)
    business_card_id = Column(String, ForeignKey("business_cards.id"), nullable=True)
    nome = Column(String, nullable=False)
    cognome = Column(String, nullable=False)
    nome_completo = Column(String, nullable=True)  # Generated field
    azienda = Column(String, nullable=True)
    posizione = Column(String, nullable=True)
    telefono = Column(String, nullable=True)
    cellulare = Column(String, nullable=True)
    email = Column(String, nullable=True)
    sito_web = Column(String, nullable=True)
    indirizzo = Column(Text, nullable=True)
    citta = Column(String, nullable=True)
    cap = Column(String, nullable=True)
    paese = Column(String, nullable=True)
    linkedin = Column(String, nullable=True)
    altri_social = Column(JSON, nullable=True)
    note = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)  # Array of tags
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_by = Column(String(255), nullable=True)
    
    # Relationships
#    business_card = relationship("BusinessCard", back_populates="contacts")
