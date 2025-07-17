# models/business_card.py
# Modello per gestione biglietti da visita - IntelligenceHUB

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, JSON
from sqlalchemy.sql import func
from app.database import Base

class BusinessCard(Base):
    """Modello per biglietti da visita"""
    __tablename__ = "business_cards"

    id = Column(String, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=True)
    
    # Dati estratti
    extracted_data = Column(JSON, nullable=True)  # Dati raw estratti
    confidence_score = Column(Float, default=0.0)
    
    # Campi parsed
    nome = Column(String(255), nullable=True)
    cognome = Column(String(255), nullable=True)
    azienda = Column(String(255), nullable=True)
    posizione = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    telefono = Column(String(100), nullable=True)
    indirizzo = Column(Text, nullable=True)
    
    # Stato processing
    status = Column(String(50), default="uploaded")  # uploaded, processing, completed, error
    processing_error = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relazioni
    company_id = Column(Integer, nullable=True)  # Link ad azienda esistente
    contact_id = Column(Integer, nullable=True)  # Link a contatto creato
    
    def __repr__(self):
        return f"<BusinessCard(id={self.id}, nome={self.nome}, azienda={self.azienda})>"
