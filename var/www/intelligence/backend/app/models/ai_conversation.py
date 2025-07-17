"""
AI Conversations model for IntelliChat session memory
"""
from sqlalchemy import Column, String, Integer, Text, JSON, Boolean, DateTime, ForeignKey
#from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class AIConversation(Base):
    __tablename__ = "ai_conversations"
    
    id = Column(String, primary_key=True)  # UUID
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    title = Column(String(255), nullable=True)
    conversation_type = Column(String(50), default="intellichat")
    messages = Column(JSON, nullable=True)  # Chat history
    context = Column(JSON, nullable=True)   # Session context
    meta_data = Column(JSON, nullable=True) # Additional metadata
    is_active = Column(Boolean, default=True)
    last_message_at = Column(DateTime, nullable=True)
    total_tokens = Column(Integer, default=0)
    total_cost = Column(Integer, default=0)  # In cents
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
#    user = relationship("User", back_populates="ai_conversations")
#    company = relationship("Company", back_populates="ai_conversations")
#    voice_sessions = relationship("VoiceSession", back_populates="conversation")

class VoiceSession(Base):
    __tablename__ = "voice_sessions"
    
    id = Column(String, primary_key=True)  # UUID
    conversation_id = Column(String, ForeignKey("ai_conversations.id"), nullable=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    audio_file_path = Column(String, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    transcript = Column(Text, nullable=True)
    confidence_score = Column(Integer, nullable=True)  # 0-100
    detected_language = Column(String(10), default="it")
    detected_intent = Column(String(100), nullable=True)
    extracted_entities = Column(JSON, nullable=True)
    suggested_actions = Column(JSON, nullable=True)
    executed_actions = Column(JSON, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    whisper_model = Column(String(50), default="whisper-1")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
#    conversation = relationship("AIConversation", back_populates="voice_sessions")
#    user = relationship("User", back_populates="voice_sessions")
