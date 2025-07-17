# schemas/chat.py
# Pydantic schemas per IntelliChat - IntelligenceHUB

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChatMessage(BaseModel):
    """Schema per messaggio chat"""
    message: str = Field(..., description="Messaggio utente")
    company_id: Optional[int] = Field(None, description="ID azienda")
    include_documents: bool = Field(False, description="Includi documenti nel context")
    max_context_docs: int = Field(5, description="Numero massimo documenti context")
    conversation_id: Optional[str] = Field(None, description="ID conversazione")

class ChatResponse(BaseModel):
    """Schema per risposta chat"""
    response: str = Field(..., description="Risposta AI")
    ai_model: str = Field(default="gpt-3.5-turbo", description="Modello AI utilizzato")
    processing_time: float = Field(default=0.0, description="Tempo elaborazione in secondi")
    conversation_id: str = Field(default="", description="ID conversazione")
    sources_used: List[str] = Field(default_factory=list, description="Fonti utilizzate")
    context_documents: Optional[List[Dict[str, Any]]] = Field(default=None, description="Documenti context")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ChatError(BaseModel):
    """Schema per errori chat"""
    error: str = Field(..., description="Messaggio errore")
    code: int = Field(default=500, description="Codice errore")
    conversation_id: str = Field(default="", description="ID conversazione")
