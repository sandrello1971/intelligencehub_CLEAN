"""
🗃️ Modelli Pydantic per Web Scraping - Fixed Version
Risolve conflitti con modelli esistenti del sistema
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class ContentType(str, Enum):
    COMPANY_INFO = "company_info"
    CONTACT_INFO = "contact_info" 
    DOCUMENT = "document"
    NEWS = "news"
    PRODUCT = "product"
    SERVICE = "service"
    OTHER = "other"

class ScrapingStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ScrapingFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ON_DEMAND = "on_demand"

class IntegrationStatus(str, Enum):
    UNPROCESSED = "unprocessed"
    MATCHED = "matched"
    IMPORTED = "imported"
    CONFLICTED = "conflicted"

class RAGProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

# === MODELLI PYDANTIC (NO SQLALCHEMY TABLES) ===

class ScrapedWebsiteModel(BaseModel):
    """Modello per siti web scrappati"""
    id: Optional[int] = None
    url: str = Field(..., description="URL del sito web")
    domain: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    last_scraped: Optional[datetime] = None
    scraping_frequency: ScrapingFrequency = ScrapingFrequency.ON_DEMAND
    is_active: bool = True
    robots_txt_allowed: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL deve iniziare con http:// o https://')
        return v

class ScrapedContentModel(BaseModel):
    """Modello per contenuti scrappati"""
    id: Optional[int] = None
    website_id: Optional[int] = None
    url: str
    title: Optional[str] = None
    content: Optional[str] = None
    content_type: ContentType = ContentType.OTHER
    content_hash: Optional[str] = None
    extracted_at: Optional[datetime] = None
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    metadata: Optional[Dict[str, Any]] = None
    knowledge_document_id: Optional[str] = None  # UUID as string
    rag_processing_status: RAGProcessingStatus = RAGProcessingStatus.PENDING
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ScrapedContactModel(BaseModel):
    """Modello per contatti estratti"""
    id: Optional[int] = None
    content_id: Optional[int] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    company: Optional[str] = None
    linkedin: Optional[str] = None
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    integration_status: IntegrationStatus = IntegrationStatus.UNPROCESSED
    matched_contact_id: Optional[int] = None
    extracted_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @validator('email')
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Email non valida')
        return v

class ScrapedCompanyModel(BaseModel):
    """Modello per aziende estratte"""
    id: Optional[int] = None
    content_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    partita_iva: Optional[str] = None
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    integration_status: IntegrationStatus = IntegrationStatus.UNPROCESSED
    matched_company_id: Optional[int] = None
    extracted_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @validator('partita_iva')
    def validate_partita_iva(cls, v):
        if v and (not v.isdigit() or len(v) != 11):
            raise ValueError('Partita IVA deve essere di 11 cifre')
        return v

class ScrapingJobModel(BaseModel):
    """Modello per job di scraping"""
    id: Optional[int] = None
    website_id: Optional[int] = None
    job_type: str = "manual_scrape"
    status: ScrapingStatus = ScrapingStatus.PENDING
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    pages_scraped: int = 0
    content_extracted: int = 0
    contacts_found: int = 0
    companies_found: int = 0
    progress_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    metadata: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None  # User ID as string
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# === REQUEST/RESPONSE MODELS ===

class WebScrapingRequest(BaseModel):
    """Request model per scraping web"""
    url: str
    auto_rag: bool = True
    scraping_options: Optional[Dict[str, Any]] = None

    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL deve iniziare con http:// o https://')
        return v

class WebScrapingResponse(BaseModel):
    """Response model per scraping web"""
    success: bool
    url: str
    content_extracted: bool = False
    knowledge_document_id: Optional[str] = None
    rag_integrated: bool = False
    message: str
    metadata: Optional[Dict[str, Any]] = None

class KnowledgeIntegrationRequest(BaseModel):
    """Request per integrazione knowledge base"""
    scraped_content_id: int
    auto_process: bool = True
    force_reprocess: bool = False

class KnowledgeIntegrationResponse(BaseModel):
    """Response per integrazione knowledge base"""
    success: bool
    scraped_content_id: int
    knowledge_document_id: Optional[str] = None
    integrated: bool = False
    message: str
    processing_stats: Optional[Dict[str, Any]] = None

