import asyncio
import logging
import uuid
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

from models.scraped_data import ScrapedContentModel, ScrapedWebsiteModel

logger = logging.getLogger(__name__)

class KnowledgeBaseIntegration:
    """
    🔗 Integrazione Web Scraping → Knowledge Base
    
    Workflow:
    1. Scraped content → knowledge_documents
    2. Chunking → document_chunks  
    3. Vector processing → Qdrant
    4. IntelliChat ready
    """
    
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.connection = None
    
    async def connect(self):
        """Connessione database"""
        try:
            self.connection = psycopg2.connect(
                host=self.db_config['host'],
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config['password']
            )
            logger.info("Knowledge base connection established")
        except Exception as e:
            logger.error(f"Knowledge base connection failed: {str(e)}")
            raise
    
    async def disconnect(self):
        """Disconnessione database"""
        if self.connection:
            self.connection.close()
    
    async def create_knowledge_document_from_scraping(
        self, 
        scraped_content: ScrapedContentModel,
        website: ScrapedWebsiteModel,
        company_id: Optional[int] = None,
        uploaded_by: str = "web_scraping_engine"
    ) -> str:
        """
        Crea knowledge document da contenuto scrapato
        
        Returns:
            UUID del documento creato
        """
        try:
            # Genera UUID per documento
            doc_id = str(uuid.uuid4())
            
            # Prepara dati documento
            url = str(scraped_content.page_url)
            domain = url.split('/')[2] if '//' in url else 'unknown'
            
            filename = f"scraped_{domain}_{scraped_content.content_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            
            # Metadata completi per scraping
            metadata = {
                "source_type": "web_scraping",
                "source_url": url,
                "website_id": website.id,
                "scraped_content_id": scraped_content.id,
                "page_title": scraped_content.page_title,
                "content_type": scraped_content.content_type,
                "extraction_method": scraped_content.extraction_method,
                "confidence_score": scraped_content.confidence_score,
                "language": scraped_content.language,
                "scraped_at": scraped_content.scraped_at.isoformat() if scraped_content.scraped_at else None,
                "company_name": website.company_name,
                "partita_iva": website.partita_iva,
                "sector": website.sector,
                "scraping_frequency": website.scraping_frequency,
                "structured_data": scraped_content.structured_data
            }
            
            # Insert knowledge document
            with self.connection.cursor() as cursor:
                query = """
                INSERT INTO knowledge_documents (
                    id, filename, content_type, file_size, content_hash,
                    extracted_text, metadata, company_id, uploaded_by
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                );
                """
                
                cursor.execute(query, (
                    doc_id,
                    filename,
                    'text/html',
                    len(scraped_content.cleaned_text or ''),
                    scraped_content.content_hash,
                    scraped_content.cleaned_text,
                    json.dumps(metadata),
                    company_id,
                    uploaded_by
                ))
                
                self.connection.commit()
            
            logger.info(f"Knowledge document created: {doc_id}")
            return doc_id
            
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Failed to create knowledge document: {str(e)}")
            raise
    
    async def create_document_chunks(
        self, 
        document_id: str, 
        content: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> List[str]:
        """
        Crea chunks per documento
        
        Returns:
            Lista di chunk IDs creati
        """
        try:
            chunks = []
            chunk_ids = []
            
            # Chunking intelligente
            start = 0
            chunk_index = 0
            
            while start < len(content):
                end = min(start + chunk_size, len(content))
                chunk_text = content[start:end].strip()
                
                if len(chunk_text) > 50:  # Minimo 50 caratteri
                    chunk_id = str(uuid.uuid4())
                    
                    # Metadata chunk
                    chunk_metadata = {
                        "chunk_index": chunk_index,
                        "start_pos": start,
                        "end_pos": end,
                        "length": len(chunk_text),
                        "created_at": datetime.now().isoformat()
                    }
                    
                    chunks.append({
                        "id": chunk_id,
                        "document_id": document_id,
                        "chunk_index": chunk_index,
                        "content_chunk": chunk_text,
                        "metadata": chunk_metadata
                    })
                    
                    chunk_ids.append(chunk_id)
                    chunk_index += 1
                
                start = end - chunk_overlap
            
            # Insert chunks in batch
            if chunks:
                with self.connection.cursor() as cursor:
                    query = """
                    INSERT INTO document_chunks (
                        id, document_id, chunk_index, content_chunk, metadata
                    ) VALUES (
                        %s, %s, %s, %s, %s
                    );
                    """
                    
                    for chunk in chunks:
                        cursor.execute(query, (
                            chunk["id"],
                            chunk["document_id"],
                            chunk["chunk_index"],
                            chunk["content_chunk"],
                            json.dumps(chunk["metadata"])
                        ))
                    
                    self.connection.commit()
            
            logger.info(f"Created {len(chunks)} chunks for document {document_id}")
            return chunk_ids
            
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Failed to create chunks: {str(e)}")
            raise
    
    async def process_scraped_content_to_knowledge_base(
        self,
        scraped_contents: List[ScrapedContentModel],
        website: ScrapedWebsiteModel,
        company_id: Optional[int] = None,
        uploaded_by: str = "web_scraping_engine"
    ) -> Dict[str, Any]:
        """
        Processa lista contenuti scrapati → Knowledge Base
        
        Returns:
            Risultati processing completi
        """
        results = {
            "documents_created": 0,
            "chunks_created": 0,
            "failed_processing": 0,
            "document_ids": [],
            "errors": []
        }
        
        for content in scraped_contents:
            try:
                # Verifica se contenuto è adatto
                if not self._is_suitable_for_knowledge_base(content):
                    continue
                
                # Crea knowledge document
                doc_id = await self.create_knowledge_document_from_scraping(
                    content, website, company_id, uploaded_by
                )
                
                results["document_ids"].append(doc_id)
                results["documents_created"] += 1
                
                # Crea chunks se c'è testo
                if content.cleaned_text:
                    chunk_ids = await self.create_document_chunks(
                        doc_id, content.cleaned_text
                    )
                    results["chunks_created"] += len(chunk_ids)
                
                # Aggiorna scraped_content con knowledge_document_id
                await self._update_scraped_content_with_doc_id(content.id, doc_id)
                
            except Exception as e:
                results["failed_processing"] += 1
                results["errors"].append(f"Content {content.id}: {str(e)}")
                logger.error(f"Failed to process content {content.id}: {str(e)}")
        
        return results
    
    def _is_suitable_for_knowledge_base(self, content: ScrapedContentModel) -> bool:
        """Verifica se contenuto è adatto per knowledge base"""
        # Verifica lunghezza minima
        if not content.cleaned_text or len(content.cleaned_text) < 100:
            return False
        
        # Verifica confidence score
        if content.confidence_score < 0.3:
            return False
        
        # Verifica tipi contenuto adatti
        suitable_types = ['company_info', 'document', 'service', 'product', 'news']
        if content.content_type not in suitable_types:
            return False
        
        return True
    
    async def _update_scraped_content_with_doc_id(self, content_id: int, doc_id: str):
        """Aggiorna scraped_content con knowledge_document_id"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE scraped_content SET knowledge_document_id = %s, rag_processed = true, rag_processing_status = 'completed' WHERE id = %s",
                    (doc_id, content_id)
                )
                self.connection.commit()
        except Exception as e:
            logger.error(f"Failed to update scraped_content {content_id}: {str(e)}")
    
    async def get_scraped_documents_for_company(self, company_id: int) -> List[Dict[str, Any]]:
        """Ottieni documenti scrapati per azienda"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                SELECT 
                    kd.*,
                    sc.page_url,
                    sc.content_type as scraping_content_type,
                    sc.confidence_score,
                    sc.scraped_at
                FROM knowledge_documents kd
                LEFT JOIN scraped_content sc ON sc.knowledge_document_id = kd.id::text
                WHERE kd.company_id = %s 
                AND kd.metadata->>'source_type' = 'web_scraping'
                ORDER BY kd.created_at DESC;
                """
                
                cursor.execute(query, (company_id,))
                documents = cursor.fetchall()
                
                return [dict(doc) for doc in documents]
                
        except Exception as e:
            logger.error(f"Failed to get scraped documents for company {company_id}: {str(e)}")
            return []
    
    async def search_scraped_content(
        self, 
        query: str, 
        company_id: Optional[int] = None,
        content_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Ricerca nei contenuti scrapati (per IntelliChat)"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Query con full-text search
                base_query = """
                SELECT 
                    kd.id,
                    kd.filename,
                    kd.extracted_text,
                    kd.metadata,
                    kd.company_id,
                    kd.created_at,
                    ts_rank(to_tsvector('italian', kd.extracted_text), plainto_tsquery('italian', %s)) as rank
                FROM knowledge_documents kd
                WHERE kd.metadata->>'source_type' = 'web_scraping'
                AND to_tsvector('italian', kd.extracted_text) @@ plainto_tsquery('italian', %s)
                """
                
                params = [query, query]
                
                if company_id:
                    base_query += " AND kd.company_id = %s"
                    params.append(company_id)
                
                if content_types:
                    base_query += " AND kd.metadata->>'content_type' = ANY(%s)"
                    params.append(content_types)
                
                base_query += " ORDER BY rank DESC, kd.created_at DESC LIMIT 10"
                
                cursor.execute(base_query, params)
                results = cursor.fetchall()
                
                return [dict(result) for result in results]
                
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []

# Factory function
def create_knowledge_base_integration() -> KnowledgeBaseIntegration:
    """Factory per knowledge base integration"""
    db_config = {
        'host': 'localhost',
        'database': 'intelligence',
        'user': 'intelligence_user',
        'password': 'intelligence_pass'
    }
    return KnowledgeBaseIntegration(db_config)
