from pydantic import BaseModel, Field, HttpUrl, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum
import uuid

# =============================================================================
# ENUMS
# =============================================================================

class ContentType(str, Enum):
    COMPANY_INFO = "company_info"
    CONTACT_INFO = "contact_info"
    DOCUMENT = "document"
    NEWS = "news"
    PRODUCT = "product"
    SERVICE = "service"
    GENERAL = "general"

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
    REJECTED = "rejected"

class RAGProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

# =============================================================================
# DATA MODELS
# =============================================================================

class ScrapedWebsiteModel(BaseModel):
    """Modello per siti web tracciati"""
    
    id: Optional[int] = None
    url: HttpUrl
    domain: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    
    # Configurazione
    scraping_frequency: ScrapingFrequency = ScrapingFrequency.WEEKLY
    max_depth: int = Field(default=1, ge=1, le=5)
    follow_external_links: bool = False
    respect_robots_txt: bool = True
    
    # Status
    status: str = "active"
    last_scraped: Optional[datetime] = None
    next_scrape_scheduled: Optional[datetime] = None
    
    # Metadata autonoma
    company_name: Optional[str] = None
    partita_iva: Optional[str] = None
    sector: Optional[str] = None
    country: str = "IT"
    
    # Audit
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    
    # Scraping metadata
    robots_txt_content: Optional[str] = None
    success_count: int = 0
    error_count: int = 0
    last_error_message: Optional[str] = None
    
    @validator('partita_iva')
    def validate_partita_iva(cls, v):
        if v and len(v) != 11:
            raise ValueError('P.IVA deve essere 11 cifre')
        return v
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class ScrapedContentModel(BaseModel):
    """Modello per contenuti estratti"""
    
    id: Optional[int] = None
    website_id: int
    
    # Identificazione
    page_url: HttpUrl
    page_title: Optional[str] = None
    content_type: ContentType
    content_hash: Optional[str] = None
    
    # Contenuto
    raw_html: Optional[str] = None
    cleaned_text: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None
    
    # Metadata
    extraction_method: Optional[str] = None
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    language: str = "it"
    
    # RAG Integration
    knowledge_document_id: Optional[uuid.UUID] = None
    rag_processed: bool = False
    rag_processing_status: RAGProcessingStatus = RAGProcessingStatus.PENDING
    rag_processing_error: Optional[str] = None
    
    # Audit
    scraped_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            uuid.UUID: lambda v: str(v) if v else None
        }

class ScrapedContactModel(BaseModel):
    """Modello per contatti estratti"""
    
    id: Optional[int] = None
    scraped_content_id: int
    
    # Dati contatto
    full_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    
    # Social
    linkedin_url: Optional[str] = None
    other_social: Optional[Dict[str, str]] = None
    
    # Metadata azienda
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    
    # Qualità
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    data_source: Optional[str] = None
    
    # Future integration
    matched_contact_id: Optional[int] = None
    integration_status: IntegrationStatus = IntegrationStatus.UNPROCESSED
    
    # Audit
    extracted_at: Optional[datetime] = None
    
    @validator('email')
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Email non valida')
        return v
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class ScrapedCompanyModel(BaseModel):
    """Modello per aziende estratte"""
    
    id: Optional[int] = None
    scraped_content_id: int
    
    # Dati azienda
    company_name: str
    description: Optional[str] = None
    sector: Optional[str] = None
    company_size: Optional[str] = None
    
    # Contatti
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    
    # Indirizzo
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_zip: Optional[str] = None
    address_country: str = "Italia"
    
    # Identificativi
    partita_iva: Optional[str] = None
    
    # Digital presence
    social_media: Optional[Dict[str, str]] = None
    
    # Business
    services_offered: Optional[List[str]] = None
    products_offered: Optional[List[str]] = None
    
    # Qualità
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    data_completeness: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Future integration
    matched_company_id: Optional[int] = None
    integration_status: IntegrationStatus = IntegrationStatus.UNPROCESSED
    
    # Audit
    extracted_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    
    @validator('partita_iva')
    def validate_partita_iva(cls, v):
        if v and len(v) != 11:
            raise ValueError('P.IVA deve essere 11 cifre')
        return v
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class ScrapingJobModel(BaseModel):
    """Modello per job di scraping"""
    
    id: Optional[int] = None
    website_id: int
    
    # Job info
    job_type: str = "scheduled"
    status: ScrapingStatus = ScrapingStatus.PENDING
    priority: int = Field(default=5, ge=1, le=10)
    
    # Execution
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    
    # Results
    pages_scraped: int = 0
    content_extracted: int = 0
    contacts_found: int = 0
    companies_found: int = 0
    rag_documents_created: int = 0
    
    # Error handling
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    # Config
    scraping_config: Optional[Dict[str, Any]] = None
    
    # Audit
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    
    # Results
    results_summary: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

# =============================================================================
# UTILITY MODELS
# =============================================================================

class ScrapingMetrics(BaseModel):
    """Metriche di scraping"""
    
    total_websites: int = 0
    active_websites: int = 0
    total_content: int = 0
    total_contacts: int = 0
    total_companies: int = 0
    rag_processed_content: int = 0
    average_confidence_score: float = 0.0
    success_rate: float = 0.0
    last_scraping_date: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class DatabaseStats(BaseModel):
    """Statistiche database"""
    
    scraped_websites_count: int = 0
    scraped_content_count: int = 0
    scraped_contacts_count: int = 0
    scraped_companies_count: int = 0
    scraping_jobs_count: int = 0
    
    # Breakdown per status
    jobs_by_status: Dict[str, int] = {}
    content_by_type: Dict[str, int] = {}
    rag_processing_stats: Dict[str, int] = {}
