from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import logging
from app.core.database import get_db
from .orchestrator import WebScrapingOrchestrator
from .document_service import DocumentService

logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/api/web-scraping-v2", tags=["Web Scraping V2"])

# Request/Response Models
class ScrapeRequest(BaseModel):
    url: HttpUrl
    
class ScrapeResponse(BaseModel):
    success: bool
    message: str
    document_id: Optional[int] = None
    title: Optional[str] = None
    chunks_created: Optional[int] = None
    chunks_vectorized: Optional[int] = None
    duplicate: Optional[bool] = None
    error: Optional[str] = None
    stage: Optional[str] = None

class DeleteRequest(BaseModel):
    url: str

class DocumentItem(BaseModel):
    id: int
    url: str
    domain: str
    title: str
    status: str
    scraped_at: str
    vectorized: bool
    vector_chunks_count: int

class StatsResponse(BaseModel):
    success: bool
    total_documents: int
    vectorized_documents: int
    total_chunks: int
    qdrant_points: int
    status: str
    error: Optional[str] = None

# API Endpoints
@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_url(request: ScrapeRequest, db: Session = Depends(get_db)):
    """
    Scraping completo con vettorizzazione automatica
    Processo atomico: tutto o niente
    """
    try:
        orchestrator = WebScrapingOrchestrator(db)
        result = orchestrator.scrape_and_process(str(request.url))
        
        if result["success"]:
            return ScrapeResponse(
                success=True,
                message=result["message"],
                document_id=result.get("document_id"),
                title=result.get("title"),
                chunks_created=result.get("chunks_created"),
                chunks_vectorized=result.get("chunks_vectorized"),
                duplicate=result.get("duplicate", False)
            )
        else:
            return ScrapeResponse(
                success=False,
                message="Scraping failed",
                error=result["error"],
                stage=result.get("stage")
            )
            
    except Exception as e:
        logger.error(f"Scrape API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/document")
async def delete_document(request: DeleteRequest, db: Session = Depends(get_db)):
    """
    Eliminazione completa documento
    Rimuove da database + Qdrant
    """
    try:
        orchestrator = WebScrapingOrchestrator(db)
        result = orchestrator.delete_document_complete(request.url)
        
        if result["success"]:
            return {"success": True, "message": result["message"]}
        else:
            raise HTTPException(status_code=404, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents", response_model=List[DocumentItem])
async def get_documents(db: Session = Depends(get_db)):
    """Lista tutti i documenti scrappati"""
    try:
        document_service = DocumentService(db)
        documents = document_service.get_all_documents()
        
        result = []
        for doc in documents:
            result.append(DocumentItem(
                id=doc.id,
                url=doc.url,
                domain=doc.domain,
                title=doc.title,
                status=doc.status,
                scraped_at=doc.scraped_at.isoformat(),
                vectorized=doc.vectorized,
                vector_chunks_count=doc.vector_chunks_count
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Documents API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    """Statistiche complete del sistema"""
    try:
        orchestrator = WebScrapingOrchestrator(db)
        stats = orchestrator.get_stats()
        
        if stats["success"]:
            return StatsResponse(
                success=True,
                total_documents=stats["total_documents"],
                vectorized_documents=stats["vectorized_documents"],
                total_chunks=stats["total_chunks"],
                qdrant_points=stats["qdrant_points"],
                status=stats["status"]
            )
        else:
            return StatsResponse(
                success=False,
                total_documents=0,
                vectorized_documents=0,
                total_chunks=0,
                qdrant_points=0,
                status="error",
                error=stats["error"]
            )
            
    except Exception as e:
        logger.error(f"Stats API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0",
        "module": "web_scraping_v2"
    }

# Test endpoints for development
@router.post("/test-scraping")
async def test_scraping_only(request: ScrapeRequest):
    """Test solo scraping senza database (per debug)"""
    try:
        from .scraping_service import ScrapingService
        scraper = ScrapingService()
        result = scraper.scrape_url(str(request.url))
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/test-vectorization/{document_id}")
async def test_vectorization(document_id: int, db: Session = Depends(get_db)):
    """Test solo vettorizzazione per documento esistente"""
    try:
        from .vector_service import VectorService
        vector_service = VectorService(db)
        result = vector_service.vectorize_document(document_id)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}
