import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from .vector_service import VectorRAGService
from .document_processor import DocumentProcessor

logger = logging.getLogger(__name__)

class KnowledgeManager:
    """
    Gestore centrale della knowledge base aziendale
    """
    
    def __init__(self):
        self.vector_service = VectorRAGService()
        self.document_processor = DocumentProcessor()
    
    async def get_company_knowledge_stats(self, company_id: int) -> Dict[str, Any]:
        """
        Statistiche knowledge base per azienda
        """
        try:
            conn = self.vector_service._get_db_connection()
            cur = conn.cursor()
            
            # Documenti totali
            cur.execute("""
                SELECT COUNT(*) as total_documents,
                       SUM(file_size) as total_size,
                       COUNT(CASE WHEN processed_at IS NOT NULL THEN 1 END) as processed_documents
                FROM knowledge_documents 
                WHERE company_id = %s
            """, (company_id,))
            
            stats = cur.fetchone()
            
            # Chunks totali
            cur.execute("""
                SELECT COUNT(*) as total_chunks
                FROM document_chunks dc
                JOIN knowledge_documents kd ON dc.document_id = kd.id
                WHERE kd.company_id = %s
            """, (company_id,))
            
            chunks_stats = cur.fetchone()
            
            conn.close()
            
            return {
                'company_id': company_id,
                'total_documents': stats[0] if stats else 0,
                'total_size': stats[1] if stats else 0,
                'processed_documents': stats[2] if stats else 0,
                'total_chunks': chunks_stats[0] if chunks_stats else 0,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting knowledge stats: {e}")
            return {
                'error': str(e)
            }
    
    async def list_documents(self, company_id: int, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        Lista documenti nella knowledge base
        """
        try:
            conn = self.vector_service._get_db_connection()
            cur = conn.cursor()
            
            # Query documenti
            cur.execute("""
                SELECT 
                    id, filename, file_size, processed_at, created_at,
                    (SELECT COUNT(*) FROM document_chunks WHERE document_id = kd.id) as chunks_count
                FROM knowledge_documents kd
                WHERE company_id = %s
                ORDER BY created_at DESC 
                LIMIT %s OFFSET %s
            """, (company_id, limit, offset))
            
            results = cur.fetchall()
            conn.close()
            
            documents = []
            for row in results:
                documents.append({
                    "id": str(row[0]),
                    "filename": row[1],
                    "file_size": row[2],
                    "processed_at": row[3].isoformat() if row[3] else None,
                    "created_at": row[4].isoformat(),
                    "chunks_count": row[5]
                })
            
            return {
                'success': True,
                'documents': documents,
                'total': len(documents),
                'limit': limit,
                'offset': offset
            }
            
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Health check del knowledge manager
        """
        vector_health = self.vector_service.health_check()
        processor_health = self.document_processor.health_check()
        
        return {
            'vector_service': vector_health,
            'document_processor': processor_health,
            'overall': vector_health['overall'] and 'error' not in processor_health
        }
