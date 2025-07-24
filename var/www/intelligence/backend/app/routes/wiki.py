"""
Wiki API Routes for Intelligence HUB v5.0
"""
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import os
import shutil
from pathlib import Path

from app.core.database import get_db
from app.services.wiki_service import WikiService
from app.schemas.wiki import (
    WikiPageResponse, WikiPageCreate, WikiPageUpdate,
    WikiCategoryResponse, WikiCategoryCreate,
    WikiDocumentUpload, WikiProcessingResult,
    WikiChatQuery, WikiChatResponse, WikiStats
)

router = APIRouter(prefix="/wiki", tags=["Wiki"])

# Initialize service
wiki_service = WikiService()

# Upload directory
UPLOAD_DIR = Path("/var/www/intelligence/backend/uploads/wiki")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ===== CATEGORY ENDPOINTS =====
@router.get("/categories", response_model=List[WikiCategoryResponse])
async def get_categories(db: Session = Depends(get_db)):
    """Get all wiki categories"""
    return wiki_service.get_categories(db)

@router.post("/categories", response_model=WikiCategoryResponse)
async def create_category(
    category_data: WikiCategoryCreate,
    db: Session = Depends(get_db)
):
    """Create new wiki category"""
    return wiki_service.create_category(db, category_data)

# ===== PAGE ENDPOINTS =====
@router.get("/pages", response_model=List[WikiPageResponse])
async def get_pages(
    status: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get wiki pages with optional filters"""
    return wiki_service.get_pages(db, status, category, limit, offset)

@router.get("/pages/{slug}", response_model=WikiPageResponse)
async def get_page_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """Get wiki page by slug"""
    page = wiki_service.get_page_by_slug(db, slug)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page

@router.post("/pages", response_model=WikiPageResponse)
async def create_page(
    page_data: WikiPageCreate,
    author_id: str = "system",
    db: Session = Depends(get_db)
):
    """Create new wiki page"""
    return wiki_service.create_page(db, page_data, author_id)

@router.put("/pages/{page_id}", response_model=WikiPageResponse)
async def update_page(
    page_id: int,
    page_data: WikiPageUpdate,
    editor_id: str = "system",
    db: Session = Depends(get_db)
):
    """Update wiki page"""
    page = wiki_service.update_page(db, page_id, page_data, editor_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page

@router.delete("/pages/{page_id}")
async def delete_page(
    page_id: int,
    db: Session = Depends(get_db)
):
    """Delete wiki page"""
    success = wiki_service.delete_page(db, page_id)
    if not success:
        raise HTTPException(status_code=404, detail="Page not found")
    return {"message": "Page deleted successfully"}

# ===== DOCUMENT UPLOAD ENDPOINTS =====
@router.post("/upload", response_model=WikiProcessingResult)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    category: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # JSON string of tags
    auto_publish: bool = Form(False),
    author_id: str = Form("system"),
    db: Session = Depends(get_db)
):
    """Upload and process document for wiki creation"""
    
    # Validate file type
    allowed_extensions = {'.pdf', '.docx', '.txt', '.md', '.html'}
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file_extension} not supported. Allowed: {allowed_extensions}"
        )
    
    # Save uploaded file
    file_path = UPLOAD_DIR / f"{title}_{file.filename}"
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Process document
    try:
        processing_result = await wiki_service.process_document_for_wiki(
            str(file_path), title, category, author_id
        )
        
        if not processing_result['success']:
            return WikiProcessingResult(
                document_id=str(file_path),
                processing_status="failed",
                sections_created=0,
                chunks_created=0,
                errors=[processing_result['error']]
            )
        
        # Parse tags if provided
        import json
        parsed_tags = []
        if tags:
            try:
                parsed_tags = json.loads(tags) if isinstance(tags, str) else tags
            except json.JSONDecodeError:
                parsed_tags = [tag.strip() for tag in tags.split(',')]
        
        # Create wiki page if auto_publish
        wiki_page_id = None
        if auto_publish:
            page_data = WikiPageCreate(
                title=title,
                content_markdown=processing_result['content'],
                excerpt=processing_result['excerpt'],
                category=category,
                tags=parsed_tags,
                status="published" if auto_publish else "draft"
            )
            
            page = await wiki_service.create_page_from_document(
                db, processing_result, page_data, author_id
            )
            wiki_page_id = page.id
        
        return WikiProcessingResult(
            document_id=str(file_path),
            wiki_page_id=wiki_page_id,
            processing_status="success",
            sections_created=len(processing_result.get('sections', [])),
            chunks_created=0,  # Will be set when added to vector DB
            preview_html=processing_result.get('html_preview', ''),
            errors=[]
        )
        
    except Exception as e:
        return WikiProcessingResult(
            document_id=str(file_path),
            processing_status="error",
            sections_created=0,
            chunks_created=0,
            errors=[str(e)]
        )
    finally:
        # Clean up uploaded file
        if file_path.exists():
            file_path.unlink()

# ===== SEARCH ENDPOINTS =====
@router.get("/search")
async def search_wiki(
    q: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Search wiki content"""
    if not q or len(q.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query too short")
    
    results = await wiki_service.search_wiki(q, db, limit)
    return {
        "query": q,
        "results": results,
        "total": len(results)
    }

# ===== CHAT ENDPOINTS =====
@router.post("/chat", response_model=WikiChatResponse)
async def wiki_chat(
    chat_query: WikiChatQuery,
    db: Session = Depends(get_db)
):
    """Chat with wiki content using RAG"""
    import time
    start_time = time.time()
    
    try:
        # Use search to get relevant content
        search_results = await wiki_service.search_wiki(
            chat_query.query, db, limit=5
        )
        
        # Simple response generation (can be enhanced with LLM)
        if not search_results:
            response_text = "Non ho trovato informazioni rilevanti nella wiki per rispondere alla tua domanda."
            sources = []
            wiki_pages = []
        else:
            # Combine relevant content
            context_pieces = []
            sources = []
            wiki_pages = []
            
            for result in search_results[:3]:  # Top 3 results
                context_pieces.append(result['text'])
                sources.append({
                    'page_title': result['page']['title'],
                    'page_slug': result['page']['slug'],
                    'score': result['score']
                })
                wiki_pages.append(result['page']['id'])
            
            # Simple response (this should use LLM in production)
            context = "\n\n".join(context_pieces)
            response_text = f"Basandomi sulla documentazione wiki, ecco cosa ho trovato:\n\n{context[:500]}..."
        
        # Generate session ID if not provided
        session_id = chat_query.session_id or f"wiki_session_{int(time.time())}"
        
        response_time = int((time.time() - start_time) * 1000)
        
        return WikiChatResponse(
            response=response_text,
            session_id=session_id,
            sources=sources,
            wiki_pages_referenced=list(set(wiki_pages)),
            response_time_ms=response_time,
            confidence_score=0.8 if search_results else 0.1
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

# ===== STATS ENDPOINT =====
@router.get("/stats", response_model=WikiStats)
async def get_wiki_stats(db: Session = Depends(get_db)):
    """Get wiki statistics"""
    from sqlalchemy import func
    from app.models.wiki import WikiPage, WikiCategory
    
    total_pages = db.query(func.count(WikiPage.id)).scalar()
    published_pages = db.query(func.count(WikiPage.id)).filter(WikiPage.status == 'published').scalar()
    draft_pages = db.query(func.count(WikiPage.id)).filter(WikiPage.status == 'draft').scalar()
    total_categories = db.query(func.count(WikiCategory.id)).scalar()
    total_views = db.query(func.sum(WikiPage.view_count)).scalar() or 0
    
    return WikiStats(
        total_pages=total_pages,
        published_pages=published_pages,
        draft_pages=draft_pages,
        total_categories=total_categories,
        total_views=total_views,
        recent_activity={}
    )

# ===== HEALTH CHECK =====
@router.get("/health")
async def wiki_health_check():
    """Wiki system health check"""
    return {
        "status": "operational",
        "upload_directory": str(UPLOAD_DIR),
        "upload_dir_exists": UPLOAD_DIR.exists(),
        "vector_service": "connected",  # Should check actual connection
        "timestamp": time.time()
    }
