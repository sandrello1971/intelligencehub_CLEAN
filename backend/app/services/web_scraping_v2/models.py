from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class ScrapedDocument(Base):
    """Modello unificato per documenti scrappati"""
    __tablename__ = "scraped_documents_v2"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, nullable=False, index=True)
    domain = Column(String, nullable=False)
    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    content_hash = Column(String, nullable=False)  # Per evitare duplicati
    status = Column(String, default="completed")  # completed, failed, processing
    scraped_at = Column(DateTime, default=datetime.utcnow)
    vectorized = Column(Boolean, default=False)
    vector_chunks_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    # Relazione con chunks
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

class DocumentChunk(Base):
    """Chunks per vettorizzazione"""
    __tablename__ = "document_chunks_v2"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("scraped_documents_v2.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    vector_id = Column(String, nullable=True)  # ID in Qdrant
    created_at = Column(DateTime, default=datetime.utcnow)
    
    document = relationship("ScrapedDocument", back_populates="chunks")
