from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
import asyncio
import logging
from datetime import datetime
from pydantic import BaseModel, HttpUrl

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/web-scraping", tags=["web-scraping"])

class ScrapeUrlRequest(BaseModel):
    url: HttpUrl
    auto_rag: bool = True

class ScrapeResponse(BaseModel):
    success: bool
    url: str
    knowledge_document_id: Optional[str] = None
    rag_integrated: bool = False
    message: str

@router.get("/health")
async def health_check():
    """Health check del Web Scraping Module"""
    return {
        "status": "operational",
        "module": "web-scraping",
        "timestamp": datetime.utcnow().isoformat(),
        "features": {
            "scraping_engine": True,
            "rag_integration": True,
            "knowledge_base": True
        }
    }

@router.post("/scrape-url", response_model=ScrapeResponse)
async def scrape_single_url(request: ScrapeUrlRequest):
    """
    Scrape singolo URL e integrazione automatica con knowledge base
    """
    try:
        url = str(request.url)
        logger.info(f"🌐 Inizio scraping URL: {url}")
        
        # Import scraping engine (lazy import per evitare conflitti)
        from .scraping_engine import IntelligenceIntelligenceWebScrapingEngine
        from .knowledge_base_integration_corrected import KnowledgeBaseIntegration
        
        # Initialize services
        scraping_engine = IntelligenceIntelligenceWebScrapingEngine()
        kb_integration = KnowledgeBaseIntegration()
        
        # Scrape content
        scraped_data = await scraping_engine.scrape_website(url)
        
        if not scraped_data:
            raise HTTPException(status_code=400, detail="Impossibile scrappare l'URL fornito")
        
        # Knowledge base integration
        if request.auto_rag:
            knowledge_doc_id = await kb_integration.create_knowledge_document_from_scraped(
                scraped_data=scraped_data,
                url=url
            )
            
            return ScrapeResponse(
                success=True,
                url=url,
                knowledge_document_id=str(knowledge_doc_id),
                rag_integrated=True,
                message="URL scrappato e integrato con successo nella knowledge base"
            )
        else:
            return ScrapeResponse(
                success=True,
                url=url,
                rag_integrated=False,
                message="URL scrappato con successo"
            )
            
    except Exception as e:
        logger.error(f"❌ Errore scraping URL {url}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Errore durante lo scraping: {str(e)}")

@router.get("/status")
async def get_scraping_status():
    """Status completo del sistema di scraping"""
    try:
        # Import database connection
        from app.database import get_db
        
        return {
            "system_status": "operational",
            "active_jobs": 0,
            "processed_sites": 0,
            "knowledge_documents": 0,
            "last_update": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Errore getting status: {str(e)}")
        return {
            "system_status": "error",
            "error": str(e),
            "last_update": datetime.utcnow().isoformat()
        }
