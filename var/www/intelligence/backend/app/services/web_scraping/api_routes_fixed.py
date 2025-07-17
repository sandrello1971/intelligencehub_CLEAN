from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional
import asyncio
import logging
from datetime import datetime

from models.scraped_data import (
    ScrapedWebsiteModel, 
    ScrapedContentModel,
    ScrapingJobModel,
    ContentType,
    ScrapingStatus
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/web-scraping", tags=["web-scraping"])

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

@router.get("/status")
async def get_scraping_status():
    """Status completo del sistema di scraping"""
    return {
        "system_status": "operational",
        "active_jobs": 0,
        "processed_sites": 0,
        "knowledge_documents": 0,
        "last_update": datetime.utcnow().isoformat()
    }

@router.post("/scrape-url")
async def scrape_single_url(
    url: str,
    auto_rag: bool = True,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Scrape singolo URL e integrazione automatica con knowledge base
    """
    try:
        logger.info(f"🌐 Inizio scraping URL: {url}")
        
        # Import scraping engine
        from scraping_engine import WebScrapingEngine
        from knowledge_base_integration_corrected import KnowledgeBaseIntegration
        
        # Initialize services
        scraping_engine = WebScrapingEngine()
        kb_integration = KnowledgeBaseIntegration()
        
        # Scrape content
        scraped_data = await scraping_engine.scrape_website(url)
        
        if not scraped_data:
            raise HTTPException(status_code=400, detail="Impossibile scrappare l'URL fornito")
        
        # Knowledge base integration
        if auto_rag:
            knowledge_doc_id = await kb_integration.create_knowledge_document_from_scraped(
                scraped_data=scraped_data,
                url=url
            )
            
            return {
                "success": True,
                "url": url,
                "content_extracted": True,
                "knowledge_document_id": str(knowledge_doc_id),
                "rag_integrated": True,
                "message": "URL scrappato e integrato con successo nella knowledge base"
            }
        else:
            return {
                "success": True,
                "url": url,
                "content_extracted": True,
                "rag_integrated": False,
                "message": "URL scrappato con successo"
            }
            
    except Exception as e:
        logger.error(f"❌ Errore scraping URL {url}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Errore durante lo scraping: {str(e)}")

@router.post("/integrate-to-knowledge")
async def integrate_scraped_to_knowledge(
    scraped_content_id: int,
    auto_process: bool = True
):
    """
    Integra contenuto scrappato esistente nella knowledge base
    """
    try:
        from knowledge_base_integration_corrected import KnowledgeBaseIntegration
        
        kb_integration = KnowledgeBaseIntegration()
        
        knowledge_doc_id = await kb_integration.integrate_existing_scraped_content(
            scraped_content_id=scraped_content_id,
            auto_process=auto_process
        )
        
        return {
            "success": True,
            "scraped_content_id": scraped_content_id,
            "knowledge_document_id": str(knowledge_doc_id),
            "integrated": True,
            "message": "Contenuto integrato con successo nella knowledge base"
        }
        
    except Exception as e:
        logger.error(f"❌ Errore integrazione knowledge base: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Errore integrazione: {str(e)}")

