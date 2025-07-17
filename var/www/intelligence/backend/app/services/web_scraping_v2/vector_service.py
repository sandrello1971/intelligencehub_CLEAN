import uuid
import asyncio
from typing import Dict, List
import logging
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import openai
import os
from sqlalchemy.orm import Session
from .models import ScrapedDocument, DocumentChunk

logger = logging.getLogger(__name__)

class VectorService:
    """Servizio dedicato alla vettorizzazione e storage in Qdrant"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.qdrant_client = QdrantClient(
            host=os.getenv("QDRANT_HOST", "localhost"),
            port=int(os.getenv("QDRANT_PORT", "6333"))
        )
        self.collection_name = "intelligence_knowledge"
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Assicura che la collection Qdrant esista"""
        try:
            collections = self.qdrant_client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if self.collection_name not in collection_names:
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"Failed to ensure Qdrant collection: {e}")
            raise
    
    def vectorize_document(self, document_id: int) -> Dict:
        """
        Vettorizza tutti i chunks di un documento
        Returns: {success: bool, vectorized_chunks: int, error: str}
        """
        try:
            # Get document and chunks
            document = self.db.query(ScrapedDocument).filter(
                ScrapedDocument.id == document_id
            ).first()
            
            if not document:
                return {"success": False, "error": "Document not found"}
            
            chunks = self.db.query(DocumentChunk).filter(
                DocumentChunk.document_id == document_id
            ).all()
            
            if not chunks:
                return {"success": False, "error": "No chunks found"}
            
            # Generate embeddings for all chunks
            vectorized_count = 0
            points = []
            
            for chunk in chunks:
                try:
                    # Generate embedding
                    embedding_response = self.openai_client.embeddings.create(
                        model="text-embedding-ada-002",
                        input=chunk.chunk_text
                    )
                    embedding = embedding_response.data[0].embedding
                    
                    # Create Qdrant point
                    import uuid
                    point_id = str(uuid.uuid4())
                    point = PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload={
                            "document_id": document_id,
                            "chunk_index": chunk.chunk_index,
                            "chunk_text": chunk.chunk_text,
                            "url": document.url,
                            "domain": document.domain,
                            "title": document.title,
                            "source": "web_scraping_v2"
                        }
                    )
                    points.append(point)
                    
                    # Update chunk with vector ID
                    chunk.vector_id = point_id
                    vectorized_count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to vectorize chunk {chunk.id}: {e}")
                    continue
            
            # Upload to Qdrant in batch
            if points:
                self.qdrant_client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )
                
                # Mark document as vectorized
                document.vectorized = True
                document.vector_chunks_count = vectorized_count
                self.db.commit()
                
                logger.info(f"Vectorized {vectorized_count} chunks for document {document_id}")
                return {
                    "success": True,
                    "vectorized_chunks": vectorized_count
                }
            else:
                return {"success": False, "error": "No chunks could be vectorized"}
                
        except Exception as e:
            self.db.rollback()
            logger.error(f"Vectorization failed for document {document_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def delete_vectors(self, document_id: int) -> Dict:
        """
        Elimina vettori dal Qdrant per un documento
        Returns: {success: bool, error: str}
        """
        try:
            # Get all vector IDs for this document
            chunks = self.db.query(DocumentChunk).filter(
                DocumentChunk.document_id == document_id,
                DocumentChunk.vector_id.isnot(None)
            ).all()
            
            vector_ids = [chunk.vector_id for chunk in chunks]
            
            if vector_ids:
                # Delete from Qdrant
                self.qdrant_client.delete(
                    collection_name=self.collection_name,
                    points_selector=vector_ids
                )
                
                logger.info(f"Deleted {len(vector_ids)} vectors for document {document_id}")
            
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Failed to delete vectors for document {document_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def search_similar(self, query: str, limit: int = 10) -> Dict:
        """
        Cerca contenuti simili nella collection
        Returns: {success: bool, results: List[dict], error: str}
        """
        try:
            # Generate query embedding
            embedding_response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=query
            )
            query_embedding = embedding_response.data[0].embedding
            
            # Search in Qdrant
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=0.7
            )
            
            results = []
            for result in search_results:
                results.append({
                    "score": result.score,
                    "content": result.payload.get("chunk_text", ""),
                    "url": result.payload.get("url", ""),
                    "title": result.payload.get("title", ""),
                    "document_id": result.payload.get("document_id")
                })
            
            return {
                "success": True,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return {"success": False, "error": str(e)}
    
    def get_collection_stats(self) -> Dict:
        """Statistiche collection Qdrant"""
        try:
            info = self.qdrant_client.get_collection(self.collection_name)
            return {
                "success": True,
                "points_count": info.points_count,
                "status": info.status
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
