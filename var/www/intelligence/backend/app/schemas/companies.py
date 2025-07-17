"""
Company Schemas for API
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum

class PartnerCategory(str, Enum):
    CLOUD_COMPUTING = "Cloud Computing"
    AI_ML = "AI/Machine Learning"
    CYBERSECURITY = "Cybersecurity"
    SOFTWARE_DEVELOPMENT = "Software Development"
    CONSULTING = "Consulting"
    MARKETING = "Marketing"
    DESIGN = "Design"
    DATA_ANALYTICS = "Data Analytics"
    INFRASTRUCTURE = "Infrastructure"
    OTHER = "Other"

class CompanyBase(BaseModel):
    name: str
    partita_iva: Optional[str] = None
    codice_fiscale: Optional[str] = None
    indirizzo: Optional[str] = None
    citta: Optional[str] = None
    provincia: Optional[str] = None
    regione: Optional[str] = None
    settore: Optional[str] = None
    numero_dipendenti: Optional[int] = None
    sito_web: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    note: Optional[str] = None

class CompanyResponse(CompanyBase):
    id: int
    codice: Optional[str] = None
    cap: Optional[str] = None
    stato: Optional[str] = None
    data_acquisizione: Optional[date] = None
    score: Optional[int] = None
    zona_commerciale: Optional[str] = None
    sales_persons: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    
    # Partner fields
    is_partner: bool = False
    is_supplier: bool = False
    partner_category: Optional[str] = None
    partner_description: Optional[str] = None
    partner_expertise: Optional[List[str]] = []
    partner_rating: float = 0.0
    partner_status: str = "active"
    
    # Scraping fields
    last_scraped_at: Optional[datetime] = None
    scraping_status: str = "pending"
    ai_analysis_summary: Optional[str] = None
    
    class Config:
        from_attributes = True

class PartnerUpdate(BaseModel):
    is_partner: Optional[bool] = None
    is_supplier: Optional[bool] = None
    partner_category: Optional[PartnerCategory] = None
    partner_description: Optional[str] = None
    partner_expertise: Optional[List[str]] = None
    partner_rating: Optional[float] = Field(None, ge=0, le=5)
    partner_status: Optional[str] = None

class CompanyUpdate(CompanyBase):
    name: Optional[str] = None
    # Include all partner fields
    is_partner: Optional[bool] = None
    is_supplier: Optional[bool] = None
    partner_category: Optional[PartnerCategory] = None
    partner_description: Optional[str] = None
    partner_expertise: Optional[List[str]] = None
    partner_rating: Optional[float] = Field(None, ge=0, le=5)

class CompanySearchResponse(BaseModel):
    companies: List[CompanyResponse]
    total: int
    partners_count: int
    suppliers_count: int
    scraped_count: int

class PartnerSearchRequest(BaseModel):
    query: str = Field(..., description="Natural language query about partners")
    category: Optional[PartnerCategory] = None
    min_rating: Optional[float] = Field(None, ge=0, le=5)
    location: Optional[str] = None
