from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import asyncio
import os
from pathlib import Path
import shutil
import uuid
from datetime import datetime

from app.core.database import get_db
from app.modules.rag_engine.knowledge_manager import KnowledgeManager
from app.modules.rag_engine.document_processor import DocumentProcessor
from app.modules.rag_engine.vector_service import VectorRAGService

router = APIRouter(prefix="/rag", tags=["RAG Knowledge Management"])

# Initialize services
km = KnowledgeManager()
doc_processor = DocumentProcessor()
vector_service = VectorRAGService()

UPLOAD_DIR = Path("/var/www/intelligence/backend/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.get("/health")
async def rag_health_check():
    """Health check completo del sistema RAG"""
    health = await km.health_check()
    
    # Test aggiuntivi
    try:
        # Test Qdrant connection
        qdrant_stats = vector_service.get_stats()
        health['qdrant_detailed'] = qdrant_stats
        
        # Test OpenAI embeddings
        test_embedding = await vector_service.generate_embeddings("test")
        health['openai_embeddings'] = f"OK - {len(test_embedding)} dimensions"
        
    except Exception as e:
        health['additional_checks_error'] = str(e)
    
    return health

@router.get("/stats")
async def get_rag_stats():
    """Statistiche complete del sistema RAG"""
    try:
        vector_stats = vector_service.get_stats()
        
        return {
            "vector_database": vector_stats,
            "supported_formats": doc_processor.get_supported_formats(),
            "upload_directory": str(UPLOAD_DIR),
            "upload_dir_exists": UPLOAD_DIR.exists(),
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "status": "error",
            "timestamp": datetime.utcnow().isoformat()
        }

@router.post("/test-embedding")
async def test_embedding(text: str = "Test document for RAG system"):
    """Test rapido generazione embeddings"""
    try:
        embedding = await vector_service.generate_embeddings(text)
        return {
            "success": True,
            "text": text,
            "embedding_dimensions": len(embedding),
            "embedding_preview": embedding[:5],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore embedding: {str(e)}")

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    company_id: int = Form(1),
    description: Optional[str] = Form(None)
):
    """Upload e processamento documento"""
    try:
        # Verifica formato supportato
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in doc_processor.get_supported_formats():
            raise HTTPException(
                status_code=400, 
                detail=f"Formato {file_extension} non supportato. Formati supportati: {doc_processor.get_supported_formats()}"
            )
        
        # Genera ID univoco per il documento
        document_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{document_id}_{file.filename}"
        file_path = UPLOAD_DIR / safe_filename
        
        # Salva file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = file_path.stat().st_size
        
        # Estrai testo dal documento
        extraction_result = await doc_processor.extract_text(file_path)
        
        return {
            "success": True,
            "message": "Documento caricato e processato con successo",
            "document_id": document_id,
            "filename": file.filename,
            "safe_filename": safe_filename,
            "size": file_size,
            "company_id": company_id,
            "description": description,
            "format": file_extension,
            "extraction": extraction_result,
            "status": "processed",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        # Cleanup file if error
        if 'file_path' in locals() and file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Errore upload: {str(e)}")

@router.post("/search")
async def semantic_search(
    request: dict
):
    """Ricerca semantica nei documenti"""
    try:
        query = request.get("query", "") or request.get("message", "")
        limit = request.get("limit", 5)
        score_threshold = request.get("score_threshold", 0.7)
        
        if not query:
            raise HTTPException(status_code=400, detail="Query richiesta")
        
        # Genera embedding per la query
        query_embedding = await vector_service.generate_embeddings(query)
        
        # Ricerca chunks in Qdrant
        search_results = await vector_service.search_similar_chunks(
            query=query,
            limit=limit
        )
        
        # Processa risultati
        relevant_docs = []
        for result in search_results:
            relevant_docs.append({
                "filename": result.get("filename", "unknown"),
                "content": result.get("content", ""),
                "score": result.get("score", 0.0),
                "source": result.get("source", "unknown")
            })
        
        # Costruisci context
        context_parts = []
        for doc in relevant_docs:
            context_parts.append(f"Documento: {doc["filename"]}\nContenuto: {doc["content"]}")
        context = "\n\n".join(context_parts)
        
        # GPT-4 call
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        system_prompt = f"""Sei un assistente AI esperto. Rispondi basandoti sui documenti forniti.\nDOCUMENTI:\n{context}\nRispondi precisamente alla domanda usando i documenti."""
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.7,
            max_tokens=600
        )
        
        ai_response = response.choices[0].message.content
        
        return {
            "query": query,
            "query_embedding_dimensions": len(query_embedding),
            "results": [],
            "total_results": 0,
            "search_params": {
                "limit": limit,
                "score_threshold": score_threshold
            },
            "status": "search_ready_pending_indexed_documents",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore ricerca: {str(e)}")

@router.get("/documents")
async def list_documents():
    """Lista documenti caricati"""
    try:
        files = list(UPLOAD_DIR.glob("*"))
        documents = []
        
        for file_path in files:
            if file_path.is_file():
                documents.append({
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                    "format": file_path.suffix.lower()
                })
        
        return {
            "documents": documents,
            "total": len(documents),
            "upload_directory": str(UPLOAD_DIR),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore lista documenti: {str(e)}")


@router.post("/chat")
async def rag_chat(request: dict):
    print(f"=== RAG CHAT REQUEST ===")
    print(f"Request: {request}")
    print(f"========================")
    """Chat con RAG - Interroga documenti usando AI"""
    try:
        query = request.get("query", "") or request.get("message", "")
        if not query:
            raise HTTPException(status_code=400, detail="Query richiesta")
        
        # Prendi TUTTI i documenti
        documents = list(UPLOAD_DIR.glob("*.txt")) + list(UPLOAD_DIR.glob("*.pdf")) + list(UPLOAD_DIR.glob("*.docx"))
        relevant_docs = []
        
        # Processa TUTTI i documenti
        for doc_path in documents:
            try:
                extraction_result = await doc_processor.extract_text(doc_path)
                if extraction_result['success'] and extraction_result['text']:
                    content_text = extraction_result['text'][:10000]
                    if len(content_text.strip()) > 50:
                        relevant_docs.append({
                            "filename": doc_path.name,
                            "content": content_text
                        })
            except Exception as e:
                print(f"Errore processing {doc_path}: {e}")
                continue
        
        # Costruisci context da TUTTI i documenti
        context_parts = []
        for doc in relevant_docs:
            context_parts.append(f"Documento: {doc['filename']}\nContenuto: {doc['content']}")
        context = "\n\n".join(context_parts)
        
        # Prompt semplice
        system_prompt = f"""Sei un assistente AI esperto. Rispondi concisamente basandoti sui documenti forniti.

DOCUMENTI:
{context}

ISTRUZIONI: Rispondi precisamente alla domanda usando i documenti. Se l'info non c'è, dillo brevemente."""

        # Chiama OpenAI
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.7,
            max_tokens=600
        )
        
        ai_response = response.choices[0].message.content
        
        return {
            "success": True,
            "query": query,
            "response": ai_response,
            "sources": [doc["filename"] for doc in relevant_docs],
            "total_docs": len(relevant_docs),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        import traceback
        print(f"=== RAG ERROR ===")
        print(f"Error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        print(f"==================")
        raise HTTPException(status_code=500, detail=f"Errore chat RAG: {str(e)}")
# Cache per documenti processati
document_cache = {}

def get_cached_document(file_path):
    """Ottieni documento dalla cache se disponibile"""
    cache_key = f"{file_path.name}_{file_path.stat().st_mtime}"
    return document_cache.get(cache_key)

def cache_document(file_path, content):
    """Salva documento in cache"""
    cache_key = f"{file_path.name}_{file_path.stat().st_mtime}"
    document_cache[cache_key] = content
    
    # Mantieni cache sotto 100 documenti
    if len(document_cache) > 100:
        oldest_key = min(document_cache.keys())
        del document_cache[oldest_key]

@router.delete("/documents/{document_id}")
async def delete_document_intelligent(document_id: str):
    """INTELLIGENT DELETE - Cancella File + Qdrant + Database"""
    try:
        # Find document file
        document_path = None
        for file_path in UPLOAD_DIR.glob("*"):
            if document_id in file_path.name:
                document_path = file_path
                break
        
        if not document_path:
            raise HTTPException(status_code=404, detail="Documento non trovato")
        
        # Delete chunks from Qdrant
        deleted_chunks = 0
        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            search_result = vector_service.qdrant_client.scroll(
                collection_name=vector_service.collection_name,
                scroll_filter=Filter(
                    must=[FieldCondition(key="filename", match=MatchValue(value=document_path.name))]
                ),
                limit=1000
            )
            
            chunk_ids = [point.id for point in search_result[0]]
            if chunk_ids:
                vector_service.qdrant_client.delete(
                    collection_name=vector_service.collection_name,
                    points_selector=chunk_ids
                )
                deleted_chunks = len(chunk_ids)
        except Exception as e:
            print(f"Warning: Qdrant cleanup failed: {e}")
        
        # Delete physical file
        document_path.unlink()
        
        return {
            "success": True,
            "message": "Documento eliminato intelligentemente", 
            "details": {
                "file_deleted": str(document_path.name),
                "qdrant_chunks_deleted": deleted_chunks
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore: {str(e)}")

@router.post("/vector-chat")
async def vector_rag_chat(request: dict):
    """Chat con RAG usando Vector Service - Nuovo endpoint sicuro"""
    try:
        query = request.get("query", "") or request.get("message", "")
        if not query:
            raise HTTPException(status_code=400, detail="Query richiesta")
        
        # USA VECTOR SERVICE
        search_results = await vector_service.search_similar_chunks(
            query, 
            limit=5, 
            score_threshold=0.3
        )
        
        # DEBUG: Print search results
        print(f"🔍 DEBUG Vector Search Results: {len(search_results)}")
        for i, result in enumerate(search_results):
            print(f"🔍 Result {i}: {result}")
        
        # Costruisci context dai risultati vector
        context_parts = []
        sources = []
        for result in search_results:
            content = result.get("content", "")
            filename = result.get("filename", "unknown")
            print(f"🔍 Processing result: filename={filename}, content_length={len(content)}, content_preview={content[:50]}")
            if content.strip():
                context_parts.append(f"Documento: {filename}\nContenuto: {content}")
                sources.append(filename)
                print(f"✅ Added to context: {filename}")
            else:
                print(f"❌ Skipped (no content): {filename}")
        
        context = "\n\n".join(context_parts)
        
        # Se non trova niente nel vector DB
        if not context.strip():
            return {
                "success": True,
                "query": query,
                "response": "Non ho trovato informazioni rilevanti nel vector database per questa query.",
                "sources": [],
                "total_docs": 0,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # GPT-4 call
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        system_prompt = f"""Sei un assistente AI esperto. Rispondi basandoti sui documenti forniti.
DOCUMENTI:
{context}
ISTRUZIONI: Rispondi precisamente alla domanda usando i documenti."""
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.7,
            max_tokens=600
        )
        
        ai_response = response.choices[0].message.content
        
        return {
            "success": True,
            "query": query,
            "response": ai_response,
            "sources": sources,
            "total_docs": len(search_results),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore RAG: {str(e)}")
