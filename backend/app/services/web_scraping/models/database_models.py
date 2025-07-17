"""
🗃️ Database Models per Web Scraping
Versione isolata senza conflitti MetaData
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

# Base separata per evitare conflitti MetaData
ScrapingBase = declarative_base()

class ScrapedWebsite(ScrapingBase):
    __tablename__ = "scraped_websites"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(2048), nullable=False, index=True)
    domain = Column(String(255), index=True)
    title = Column(String(500))
    description = Column(Text)
    status = Column(String(50), default="pending")
    last_scraped = Column(DateTime)
    scraping_frequency = Column(String(50), default="on_demand")
    robots_txt_compliant = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class ScrapedContent(ScrapingBase):
    __tablename__ = "scraped_content"
    
    id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, ForeignKey("scraped_websites.id"))
    url = Column(String(2048), nullable=False)
    title = Column(String(500))
    content_text = Column(Text)
    content_type = Column(String(100), default="webpage")
    content_hash = Column(String(64), index=True)
    confidence_score = Column(Float, default=0.0)
    knowledge_document_id = Column(UUID(as_uuid=True), index=True)
    rag_processing_status = Column(String(50), default="pending")
    metadata = Column(JSONB, default={})
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
