"""
🧠 Intellichat Route Enhancement con Web Scraping
Estende l'intellichat esistente con capacità di web scraping
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, Any, Optional
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Router per enhancement intellichat
router = APIRouter(prefix="/web-scraping", tags=["intellichat-enhanced"])

class ChatMessage(BaseModel):
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    has_webscraping: bool = False
    webscraping_data: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None

@router.post("/chat-enhanced", response_model=ChatResponse)
async def chat_with_webscraping(chat_message: ChatMessage):
    """
    Chat intellichat potenziato con web scraping
    """
    try:
        from services.intellichat_webscraping_final import handle_webscraping_in_chat_final
        
        # Check per web scraping
        webscraping_result = await handle_webscraping_in_chat_final(
            chat_message.message, 
            chat_message.user_id
        )
        
        has_webscraping = webscraping_result.get("has_webscraping", False)
        
        if has_webscraping:
            # Se ha web scraping, restituisci il risultato del scraping
            return ChatResponse(
                response=webscraping_result.get("message", "Operazione completata"),
                has_webscraping=True,
                webscraping_data=webscraping_result,
                session_id=chat_message.session_id
            )
        else:
            # Se non ha web scraping, prosegui con intellichat normale
            # Qui dovresti chiamare il tuo intellichat esistente
            return ChatResponse(
                response=f"Messaggio ricevuto: {chat_message.message}",
                has_webscraping=False,
                session_id=chat_message.session_id
            )
            
    except Exception as e:
        logger.error(f"Errore chat enhanced: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Errore nel processamento del messaggio: {str(e)}")

@router.post("/webscraping-command")
async def webscraping_command(chat_message: ChatMessage):
    """
    Endpoint dedicato per comandi di web scraping
    """
    try:
        from services.intellichat_webscraping_final import handle_webscraping_in_chat_final
        
        result = await handle_webscraping_in_chat_final(
            chat_message.message,
            chat_message.user_id
        )
        
        return {
            "success": True,
            "result": result,
            "message": result.get("message", "Comando processato")
        }
        
    except Exception as e:
        logger.error(f"Errore webscraping command: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/webscraping-stats")
async def get_webscraping_stats():
    """
    Statistiche web scraping per l'intellichat
    """
    try:
        from services.web_scraping.knowledge_base_integration_isolated import kb_integration_isolated
        
        stats = await kb_integration_isolated.get_knowledge_document_stats()
        
        return {
            "total_documents": stats.get("total_documents", 0),
            "scraped_documents": stats.get("scraped_documents", 0),
            "total_chunks": stats.get("total_chunks", 0),
            "webscraping_available": True,
            "last_update": stats.get("last_update")
        }
        
    except Exception as e:
        logger.error(f"Errore webscraping stats: {str(e)}")
        return {
            "webscraping_available": False,
            "error": str(e)
        }

# Frontend compatibility endpoints
@router.get("/scraped-sites")
async def get_scraped_sites():
    """Get list of scraped websites - Frontend compatibility"""
    return {
        "scraped_sites": [],
        "total": 0,
        "message": "WebScraping endpoint working - scraped-sites"
    }

@router.get("/knowledge-stats") 
async def get_knowledge_stats():
    """Get knowledge base statistics - Frontend compatibility"""
    return {
        "total_documents": 0,
        "scraped_documents": 0,
        "uploaded_documents": 0,
        "total_size": "0 MB",
        "message": "Knowledge stats endpoint working"
    }

@router.post("/scrape-url")
async def scrape_url(data: dict):
    """Scrape a new URL - Frontend compatibility"""
    return {
        "status": "success",
        "message": "URL scraping endpoint working",
        "url": data.get("url", ""),
        "scraped": False
    }

@router.get("/health")
async def webscraping_health():
    """WebScraping health check"""
    return {
        "status": "healthy",
        "service": "WebScraping",
        "endpoints": ["scraped-sites", "knowledge-stats", "scrape-url"],
        "version": "5.0.0"
    }
