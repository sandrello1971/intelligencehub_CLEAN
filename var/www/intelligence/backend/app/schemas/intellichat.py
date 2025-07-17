from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class ChatRequest(BaseModel):
    message: str
    company_id: Optional[int] = None
    conversation_id: Optional[str] = None
    include_documents: bool = True
    max_context_docs: int = 5

class DocumentContext(BaseModel):
    document_id: int
    filename: str
    relevance_score: float
    matched_content: str
    page_number: Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    sources: List[DocumentContext]
    ai_model: str
    processing_time: float
    tokens_used: Optional[int] = None
    
class ConversationHistory(BaseModel):
    conversation_id: str
    messages: List[ChatMessage]
    company_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

class DocumentSummary(BaseModel):
    document_id: int
    filename: str
    main_topics: List[str]
    key_points: List[str]
    mathematical_content: Optional[List[str]] = None
    document_type: str
    confidence_score: float
