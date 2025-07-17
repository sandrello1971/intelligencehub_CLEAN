from sqlalchemy.orm import Session
from typing import Dict, List, Optional
import logging
from .models import ScrapedDocument, DocumentChunk
import hashlib

logger = logging.getLogger(__name__)

class DocumentService:
    """Servizio dedicato alla gestione database documenti"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def save_document(self, scraping_data: Dict) -> Dict:
        """
        Salva documento nel database
        Returns: {success: bool, document_id: int, error: str}
        """
        try:
            # Sanitize content - remove NULL bytes
            content = scraping_data["content"].replace("\x00", "").replace("\0", "")
            scraping_data["content"] = content
            
            # Check for duplicates
            existing = self.db.query(ScrapedDocument).filter(
                ScrapedDocument.content_hash == scraping_data["content_hash"]
            ).first()
            
            if existing:
                logger.info(f"Document already exists: {scraping_data['url']}")
                return {
                    "success": True,
                    "document_id": existing.id,
                    "duplicate": True
                }
            
            # Create new document
            document = ScrapedDocument(
                url=scraping_data["url"],
                domain=scraping_data["domain"],
                title=scraping_data["title"],
                content=content,
                content_hash=scraping_data["content_hash"],
                status="completed"
            )
            
            self.db.add(document)
            self.db.commit()
            self.db.refresh(document)
            
            logger.info(f"Document saved: ID {document.id}")
            return {
                "success": True,
                "document_id": document.id,
                "duplicate": False
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to save document: {e}")
            return {"success": False, "error": str(e)}
    
    def create_chunks(self, document_id: int, content: str, chunk_size: int = 1000) -> Dict:
        """
        Crea chunks del documento per vettorizzazione
        Returns: {success: bool, chunks_count: int, chunks: List[dict]}
        """
        try:
            # Split content into chunks
            chunks = []
            words = content.split()
            
            for i in range(0, len(words), chunk_size):
                chunk_text = ' '.join(words[i:i + chunk_size])
                if len(chunk_text.strip()) > 50:  # Skip very small chunks
                    chunk = DocumentChunk(
                        document_id=document_id,
                        chunk_index=len(chunks),
                        chunk_text=chunk_text
                    )
                    chunks.append(chunk)
                    self.db.add(chunk)
            
            self.db.commit()
            
            # Update document chunks count
            document = self.db.query(ScrapedDocument).filter(
                ScrapedDocument.id == document_id
            ).first()
            if document:
                document.vector_chunks_count = len(chunks)
                self.db.commit()
            
            logger.info(f"Created {len(chunks)} chunks for document {document_id}")
            return {
                "success": True,
                "chunks_count": len(chunks),
                "chunks": [{"id": c.id, "text": c.chunk_text} for c in chunks]
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create chunks: {e}")
            return {"success": False, "error": str(e)}
    
    def delete_document(self, document_id: int) -> Dict:
        """
        Elimina documento e tutti i chunks correlati
        Returns: {success: bool, error: str}
        """
        try:
            document = self.db.query(ScrapedDocument).filter(
                ScrapedDocument.id == document_id
            ).first()
            
            if not document:
                return {"success": False, "error": "Document not found"}
            
            # Cascading delete will handle chunks automatically
            self.db.delete(document)
            self.db.commit()
            
            logger.info(f"Document {document_id} deleted successfully")
            return {"success": True}
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete document {document_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_document_by_url(self, url: str) -> Optional[ScrapedDocument]:
        """Trova documento per URL"""
        return self.db.query(ScrapedDocument).filter(
            ScrapedDocument.url == url
        ).first()
    
    def get_all_documents(self) -> List[ScrapedDocument]:
        """Lista tutti i documenti"""
        return self.db.query(ScrapedDocument).order_by(
            ScrapedDocument.scraped_at.desc()
        ).all()
