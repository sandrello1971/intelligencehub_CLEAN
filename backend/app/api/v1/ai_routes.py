"""
AI Routes - REST API per IntelliChat (New Module)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.routes.auth import get_current_user_profile as get_current_user
from app.models.users import User
from app.modules.ai.chat_service import chat_service

router = APIRouter(prefix="/ai-new", tags=["AI Services New"])

class ChatMessageRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    company_id: Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    usage: dict
    timestamp: str

@router.post("/chat", response_model=ChatResponse)
async def send_chat_message(
    request: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Endpoint principale per chat con IntelliChat (New Module)"""
    
    try:
        result = await chat_service.process_message(
            message=request.message,
            user_id=current_user.id,
            db=db,
            company_id=request.company_id
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
        
        return ChatResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore nel servizio chat: {str(e)}"
        )

@router.get("/health")
async def ai_health_check():
    """Health check per servizi AI (New Module)"""
    return {
        "status": "healthy",
        "service": "IntelliChat AI New Module",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }
