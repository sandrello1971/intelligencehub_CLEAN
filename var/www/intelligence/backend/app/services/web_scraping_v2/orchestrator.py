from sqlalchemy.orm import Session
from typing import Dict
import logging
from .scraping_service import ScrapingService
from .document_service import DocumentService
from .vector_service import VectorService

logger = logging.getLogger(__name__)

class WebScrapingOrchestrator:
    """Orchestratore che coordina scraping, database e vettorizzazione"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.scraping_service = ScrapingService()
        self.document_service = DocumentService(db_session)
        self.vector_service = VectorService(db_session)
    
    def scrape_and_process(self, url: str) -> Dict:
        """
        Processo completo: scraping + database + vettorizzazione
        ATOMICO: tutto o niente
        """
        document_id = None
        
        try:
            logger.info(f"Starting complete scraping process for: {url}")
            
            # STEP 1: Scraping
            scraping_result = self.scraping_service.scrape_url(url)
            if not scraping_result["success"]:
                return {
                    "success": False,
                    "error": f"Scraping failed: {scraping_result['error']}",
                    "stage": "scraping"
                }
            
            scraping_data = scraping_result["data"]
            logger.info(f"Scraping completed: {scraping_data['title']}")
            
            # STEP 2: Save to database
            save_result = self.document_service.save_document(scraping_data)
            if not save_result["success"]:
                return {
                    "success": False,
                    "error": f"Database save failed: {save_result['error']}",
                    "stage": "database"
                }
            
            document_id = save_result["document_id"]
            is_duplicate = save_result.get("duplicate", False)
            
            if is_duplicate:
                logger.info(f"Document is duplicate, skipping vectorization")
                return {
                    "success": True,
                    "message": "Document already exists",
                    "document_id": document_id,
                    "duplicate": True
                }
            
            logger.info(f"Document saved with ID: {document_id}")
            
            # STEP 3: Create chunks
            chunks_result = self.document_service.create_chunks(
                document_id, 
                scraping_data["content"]
            )
            if not chunks_result["success"]:
                # Rollback document
                self.document_service.delete_document(document_id)
                return {
                    "success": False,
                    "error": f"Chunking failed: {chunks_result['error']}",
                    "stage": "chunking"
                }
            
            chunks_count = chunks_result["chunks_count"]
            logger.info(f"Created {chunks_count} chunks")
            
            # STEP 4: Vectorization
            vector_result = self.vector_service.vectorize_document(document_id)
            if not vector_result["success"]:
                # Rollback document and chunks
                self.document_service.delete_document(document_id)
                return {
                    "success": False,
                    "error": f"Vectorization failed: {vector_result['error']}",
                    "stage": "vectorization"
                }
            
            vectorized_chunks = vector_result["vectorized_chunks"]
            logger.info(f"Vectorized {vectorized_chunks} chunks")
            
            # SUCCESS!
            return {
                "success": True,
                "message": f"Complete processing successful: {scraping_data['title']}",
                "document_id": document_id,
                "url": url,
                "title": scraping_data["title"],
                "chunks_created": chunks_count,
                "chunks_vectorized": vectorized_chunks,
                "duplicate": False
            }
            
        except Exception as e:
            logger.error(f"Orchestrator failed for {url}: {e}")
            
            # Cleanup on error
            if document_id:
                try:
                    self.vector_service.delete_vectors(document_id)
                    self.document_service.delete_document(document_id)
                except Exception as cleanup_error:
                    logger.error(f"Cleanup failed: {cleanup_error}")
            
            return {
                "success": False,
                "error": f"Processing failed: {str(e)}",
                "stage": "orchestration"
            }
    
    def delete_document_complete(self, url: str) -> Dict:
        """
        Eliminazione completa: database + vettori
        """
        try:
            # Find document
            document = self.document_service.get_document_by_url(url)
            if not document:
                return {"success": False, "error": "Document not found"}
            
            document_id = document.id
            
            # Delete vectors first
            vector_delete = self.vector_service.delete_vectors(document_id)
            if not vector_delete["success"]:
                logger.warning(f"Vector deletion failed: {vector_delete['error']}")
            
            # Delete from database (cascades to chunks)
            db_delete = self.document_service.delete_document(document_id)
            if not db_delete["success"]:
                return db_delete
            
            return {
                "success": True,
                "message": f"Document completely deleted: {url}"
            }
            
        except Exception as e:
            logger.error(f"Complete deletion failed for {url}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_stats(self) -> Dict:
        """Statistiche complete del sistema"""
        try:
            documents = self.document_service.get_all_documents()
            vector_stats = self.vector_service.get_collection_stats()
            
            total_docs = len(documents)
            vectorized_docs = len([d for d in documents if d.vectorized])
            total_chunks = sum(d.vector_chunks_count for d in documents)
            
            return {
                "success": True,
                "total_documents": total_docs,
                "vectorized_documents": vectorized_docs,
                "total_chunks": total_chunks,
                "qdrant_points": vector_stats.get("points_count", 0) if vector_stats["success"] else 0,
                "status": "active" if total_docs > 0 else "inactive"
            }
            
        except Exception as e:
            logger.error(f"Stats calculation failed: {e}")
            return {"success": False, "error": str(e)}
