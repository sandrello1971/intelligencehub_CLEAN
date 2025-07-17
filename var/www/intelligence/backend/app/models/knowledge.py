from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
#from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base

class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    content_hash = Column(String, nullable=False)
    company_id = Column(Integer, nullable=True)
    uploaded_by = Column(String, nullable=False)
    upload_date = Column(DateTime, default=func.now())
    processed = Column(Boolean, default=False)
    processing_status = Column(String, default="pending")
    meta_data = Column(JSON, default=dict)
    
    # Relationship
#    chunks = relationship("DocumentChunk", back_populates="document")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("knowledge_documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)
    chunk_tokens = Column(Integer, nullable=True)
    embedding_vector = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationship
#    document = relationship("KnowledgeDocument", back_populates="chunks")
