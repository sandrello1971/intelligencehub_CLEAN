# schemas/business_card.py
# Pydantic schemas per Business Cards - IntelligenceHUB

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime

class BusinessCardBase(BaseModel):
    """Base schema per business cards"""
    filename: str = Field(..., description="Nome file")
    original_filename: Optional[str] = Field(None, description="Nome file originale")
    
    # Dati estratti
    nome: Optional[str] = Field(None, description="Nome persona")
    cognome: Optional[str] = Field(None, description="Cognome persona")
    azienda: Optional[str] = Field(None, description="Nome azienda")
    posizione: Optional[str] = Field(None, description="Posizione/ruolo")
    email: Optional[str] = Field(None, description="Email")
    telefono: Optional[str] = Field(None, description="Telefono")
    indirizzo: Optional[str] = Field(None, description="Indirizzo")
    
    # Metadata
    confidence_score: float = Field(0.0, ge=0.0, le=1.0, description="Confidence score")
    status: str = Field("uploaded", description="Status elaborazione")

class BusinessCardCreate(BusinessCardBase):
    """Schema per creazione business card"""
    pass

class BusinessCardResponse(BusinessCardBase):
    """Schema per risposta business card"""
    id: str
    extracted_data: Optional[Dict[str, Any]] = None
    processing_error: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    company_id: Optional[int] = None
    contact_id: Optional[int] = None

    class Config:
        from_attributes = True  # Updated from orm_mode

class BusinessCardUpload(BaseModel):
    """Schema per upload business card"""
    filename: str = Field(..., description="Nome file")
    
class BusinessCardStats(BaseModel):
    """Schema per statistiche business cards"""
    total: int = Field(0, description="Totale business cards")
    by_status: Dict[str, int] = Field(default_factory=dict, description="Conteggio per status")
    avg_confidence: float = Field(0.0, description="Confidence score medio")

class BusinessCardListResponse(BaseModel):
    """Schema per lista business cards"""
    business_cards: List[BusinessCardResponse] = Field(default_factory=list)
    total: int = Field(0, description="Totale record")
    stats: BusinessCardStats = Field(default_factory=BusinessCardStats)
