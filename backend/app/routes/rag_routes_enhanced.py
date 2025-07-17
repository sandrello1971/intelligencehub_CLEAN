from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime

# Import esistenti RAG
from ..modules.rag_engine.vector_service import VectorRAGService
from ..modules.rag_engine.document_processor import DocumentProcessor

# Import Web Scraping
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../services/web_scraping'))

from models.scraped_data import ScrapedWebsiteModel
from scraping_engine import IntelligenceWebScrapingEngine
from rag_integration_simple import SimpleRAGIntegration

router = APIRouter(prefix="/api/rag", tags=["rag"])

# Istanze servizi
vector_service = VectorRAGService()
document_processor = DocumentProcessor()
scraping_rag = SimpleRAGIntegration()

@router.post("/upload-document")
async def upload_document(
    file: UploadFile = File(...),
    company_id: Optional[str] = Form(None),
    user_id: str = Form(...)
):
    """Upload documento tradizionale (esistente)"""
    # Logica upload esistente
    pass

@router.post("/scrape-website")
async def scrape_website_for_rag(
    url: str = Form(...),
    company_name: Optional[str] = Form(None),
    company_id: Optional[int] = Form(None),
    content_types: List[str] = Form(["company_info"]),
    auto_rag_processing: bool = Form(True),
    user_id: str = Form(...)
):
    """
    🕷️ Scraping sito web con integrazione automatica RAG
    
    Workflow:
    1. Scraping del sito
    2. Estrazione contenuti
    3. Creazione knowledge documents
    4. Embedding generation per Qdrant
    5. Integrazione con IntelliChat
    """
    try:
        # 1. Preparazione website model
        website_data = ScrapedWebsiteModel(
            id=1,  # Temporaneo
            url=url,
            company_name=company_name,
            created_by=user_id
        )
        
        # 2. Esecuzione scraping
        async with IntelligenceWebScrapingEngine(rate_limit_delay=1.0) as engine:
            scraping_results = await engine.scrape_website(website_data)
        
        if scraping_results['status'].value != 'completed':
            raise HTTPException(
                status_code=400, 
                detail=f"Scraping failed: {scraping_results.get('errors', [])}"
            )
        
        # 3. Processamento RAG se richiesto
        rag_results = []
        knowledge_docs_created = []
        
        if auto_rag_processing and scraping_results.get('content_extracted'):
            for content in scraping_results['content_extracted']:
                try:
                    # Converte in dict per RAG processing
                    content_dict = content.model_dump() if hasattr(content, 'model_dump') else content
                    
                    # Processa per RAG
                    rag_result = await scraping_rag.process_content_for_rag(content_dict)
                    rag_results.append(rag_result)
                    
                    # Se successo, crea knowledge document reale
                    if rag_result['processing_status'] == 'completed':
                        knowledge_doc = await _create_knowledge_document_from_scraped(
                            content_dict, company_id, user_id
                        )
                        knowledge_docs_created.append(knowledge_doc)
                        
                        # Processa per vector store (Qdrant)
                        await _process_for_vector_store(knowledge_doc, content_dict)
                
                except Exception as e:
                    rag_results.append({
                        'processing_status': 'failed',
                        'error': str(e)
                    })
        
        # 4. Response completa
        return {
            "success": True,
            "message": f"Scraping completato per {url}",
            "scraping_results": {
                "pages_scraped": scraping_results.get('pages_scraped', 0),
                "content_extracted": len(scraping_results.get('content_extracted', [])),
                "contacts_found": len(scraping_results.get('contacts_found', [])),
                "companies_found": len(scraping_results.get('companies_found', []))
            },
            "rag_integration": {
                "documents_created": len(knowledge_docs_created),
                "successful_integrations": len([r for r in rag_results if r.get('processing_status') == 'completed']),
                "failed_integrations": len([r for r in rag_results if r.get('processing_status') == 'failed'])
            },
            "knowledge_documents": knowledge_docs_created,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping RAG integration failed: {str(e)}")

async def _create_knowledge_document_from_scraped(
    content_dict: Dict[str, Any], 
    company_id: Optional[int],
    user_id: str
) -> Dict[str, Any]:
    """Crea knowledge document da contenuto scrapato"""
    
    # Genera filename significativo
    url = content_dict.get('page_url', 'unknown')
    domain = url.split('/')[2] if '//' in url else 'unknown'
    content_type = content_dict.get('content_type', 'general')
    
    filename = f"scraped_{domain}_{content_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    
    # Prepara dati documento
    document_data = {
        'filename': filename,
        'original_filename': filename,
        'file_type': 'html',
        'file_size': len(content_dict.get('cleaned_text', '')),
        'content_hash': content_dict.get('content_hash', ''),
        'company_id': company_id,
        'uploaded_by': user_id,
        'processing_status': 'completed',
        'meta_data': {
            'source_type': 'web_scraping',
            'source_url': url,
            'scraping_date': content_dict.get('scraped_at'),
            'content_type': content_type,
            'confidence_score': content_dict.get('confidence_score', 0),
            'page_title': content_dict.get('page_title'),
            'extraction_method': content_dict.get('extraction_method', 'playwright')
        }
    }
    
    # In implementazione reale, usa il document_processor esistente
    # Per ora ritorna dati simulati
    return {
        'id': f"doc_{datetime.now().timestamp()}",
        'filename': filename,
        'status': 'processed',
        'content_preview': content_dict.get('cleaned_text', '')[:200] + '...',
        **document_data
    }

async def _process_for_vector_store(knowledge_doc: Dict[str, Any], content_dict: Dict[str, Any]):
    """Processa documento per vector store (Qdrant)"""
    try:
        # In implementazione reale, usa vector_service esistente
        # Per ora simula il processo
        
        text = content_dict.get('cleaned_text', '')
        if len(text) > 100:
            # Simula chunking e embedding
            chunks = [text[i:i+1000] for i in range(0, len(text), 800)]
            
            for i, chunk in enumerate(chunks):
                # Simula creazione embedding
                # vector_service.create_embedding(chunk, knowledge_doc['id'], i)
                pass
        
        return True
    except Exception as e:
        print(f"Vector store processing failed: {e}")
        return False

@router.get("/scraped-documents")
async def get_scraped_documents(company_id: Optional[int] = None):
    """Ottieni documenti da web scraping nella knowledge base"""
    try:
        # Query documenti scrapati dalla knowledge base
        # In implementazione reale, query dal database
        
        return {
            "success": True,
            "documents": [
                {
                    "id": "doc_1",
                    "filename": "scraped_example.com_company_info.html",
                    "source_url": "https://example.com",
                    "company_id": company_id,
                    "created_at": datetime.now().isoformat(),
                    "content_type": "company_info",
                    "status": "processed"
                }
            ],
            "total": 1
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search-scraped-content")
async def search_scraped_content(
    query: str = Form(...),
    company_id: Optional[int] = Form(None),
    content_types: List[str] = Form(["company_info"])
):
    """
    🔍 Ricerca nei contenuti scrapati per IntelliChat
    
    Integrazione con vector search per AI chat
    """
    try:
        # In implementazione reale, usa vector_service per ricerca semantica
        # Per ora simula risultati
        
        results = [
            {
                "content": "Informazioni aziendali estratte da scraping...",
                "source_url": "https://example.com/about",
                "company_name": "Example Company",
                "content_type": "company_info",
                "confidence_score": 0.85,
                "scraped_at": datetime.now().isoformat()
            }
        ]
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "total_results": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
