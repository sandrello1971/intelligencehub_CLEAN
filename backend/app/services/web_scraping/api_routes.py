from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime

from models.scraped_data import (
    ScrapedWebsiteModel, 
    ScrapingStatus,
    ContentType,
    ScrapingFrequency
)
from scraping_engine import IntelligenceWebScrapingEngine
from rag_integration_simple import SimpleRAGIntegration

router = APIRouter(prefix="/api/web-scraping", tags=["web-scraping"])

# Global instances
rag_integration = SimpleRAGIntegration()

@router.get("/health")
async def health_check():
    """🏥 Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "intelligence-web-scraping",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@router.post("/scrape-website")
async def scrape_website(website_data: Dict[str, Any]):
    """
    🕷️ Scrape singolo website
    
    Body example:
    {
        "url": "https://example.com",
        "company_name": "Example Company",
        "respect_robots_txt": true,
        "auto_rag_processing": true
    }
    """
    try:
        # Validazione e creazione modello
        website_model = ScrapedWebsiteModel(
            id=website_data.get('id', 1),
            url=website_data['url'],
            company_name=website_data.get('company_name'),
            respect_robots_txt=website_data.get('respect_robots_txt', True),
            scraping_frequency=website_data.get('scraping_frequency', 'on_demand')
        )
        
        # Esegui scraping
        async with IntelligenceWebScrapingEngine(rate_limit_delay=1.0) as engine:
            scraping_results = await engine.scrape_website(website_model)
        
        # RAG processing se richiesto
        rag_results = None
        auto_rag = website_data.get('auto_rag_processing', False)
        
        if auto_rag and scraping_results.get('content_extracted'):
            rag_results = []
            for content in scraping_results['content_extracted']:
                content_dict = content.model_dump() if hasattr(content, 'model_dump') else content
                rag_result = await rag_integration.process_content_for_rag(content_dict)
                rag_results.append(rag_result)
        
        return {
            "success": True,
            "scraping_results": scraping_results,
            "rag_results": rag_results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@router.post("/scrape-bulk")
async def scrape_bulk_websites(websites_data: List[Dict[str, Any]]):
    """
    🕷️ Scrape multiple websites in parallel
    
    Body example:
    [
        {"url": "https://example1.com", "company_name": "Company 1"},
        {"url": "https://example2.com", "company_name": "Company 2"}
    ]
    """
    try:
        results = []
        
        # Limita concorrenza per evitare overload
        semaphore = asyncio.Semaphore(3)
        
        async def scrape_single(website_data):
            async with semaphore:
                return await scrape_website(website_data)
        
        # Esegui scraping in parallelo
        tasks = [scrape_single(data) for data in websites_data]
        bulk_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Processa risultati
        successful = 0
        failed = 0
        
        for i, result in enumerate(bulk_results):
            if isinstance(result, Exception):
                results.append({
                    "website_index": i,
                    "success": False,
                    "error": str(result)
                })
                failed += 1
            else:
                results.append({
                    "website_index": i,
                    "success": True,
                    "data": result
                })
                successful += 1
        
        return {
            "success": True,
            "total_websites": len(websites_data),
            "successful": successful,
            "failed": failed,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk scraping failed: {str(e)}")

@router.get("/stats")
async def get_scraping_stats():
    """📊 Ottieni statistiche generali scraping"""
    try:
        # Statistiche RAG
        rag_stats = rag_integration.get_stats()
        
        # Simula statistiche database (in implementazione reale, query dal DB)
        db_stats = {
            "websites_total": 0,
            "content_total": 0,
            "contacts_total": 0,
            "companies_total": 0,
            "jobs_total": 0
        }
        
        return {
            "success": True,
            "rag_stats": rag_stats,
            "database_stats": db_stats,
            "system_info": {
                "service_version": "1.0.0",
                "last_updated": datetime.now().isoformat(),
                "status": "operational"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")

@router.post("/rag/process-content")
async def process_content_for_rag(content_data: Dict[str, Any]):
    """
    🔗 Processa contenuto per RAG integration
    
    Body example:
    {
        "id": 1,
        "cleaned_text": "Contenuto da processare...",
        "content_type": "company_info",
        "confidence_score": 0.85
    }
    """
    try:
        result = await rag_integration.process_content_for_rag(content_data)
        
        return {
            "success": True,
            "rag_processing_result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG processing failed: {str(e)}")

@router.get("/rag/stats")
async def get_rag_stats():
    """📈 Ottieni statistiche RAG integration"""
    try:
        stats = rag_integration.get_stats()
        
        return {
            "success": True,
            "rag_stats": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG stats failed: {str(e)}")

@router.post("/test/scrape-demo")
async def test_scrape_demo():
    """
    🧪 Endpoint di test per demo scraping
    Scrape example.com per testing
    """
    try:
        demo_website = {
            "url": "https://example.com",
            "company_name": "Example Demo Company",
            "respect_robots_txt": True,
            "auto_rag_processing": True
        }
        
        result = await scrape_website(demo_website)
        
        return {
            "success": True,
            "message": "Demo scraping completed successfully",
            "demo_results": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo scraping failed: {str(e)}")

@router.get("/content-types")
async def get_content_types():
    """📋 Lista tipi di contenuto supportati"""
    return {
        "success": True,
        "content_types": [
            {"value": "company_info", "label": "Company Information"},
            {"value": "contact_info", "label": "Contact Information"},
            {"value": "document", "label": "Document"},
            {"value": "news", "label": "News Article"},
            {"value": "product", "label": "Product Information"},
            {"value": "service", "label": "Service Information"},
            {"value": "general", "label": "General Content"}
        ],
        "scraping_frequencies": [
            {"value": "daily", "label": "Daily"},
            {"value": "weekly", "label": "Weekly"},
            {"value": "monthly", "label": "Monthly"},
            {"value": "on_demand", "label": "On Demand"}
        ]
    }

# Error handlers
@router.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return HTTPException(status_code=400, detail=str(exc))

@router.exception_handler(ConnectionError)
async def connection_error_handler(request, exc):
    return HTTPException(status_code=503, detail="Service temporarily unavailable")
