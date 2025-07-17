"""
🔗 Knowledge Base Integration - CHUNKS COLUMN FIXED
"""

import logging
import uuid
import hashlib
import json
from datetime import datetime
from typing import Dict, Any, Optional
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class KnowledgeBaseIntegrationChunksFixed:
    
    def __init__(self):
        self.db_config = {
            "user": os.getenv("DB_USER", "intelligence_user"),
            "password": os.getenv("DB_PASSWORD", "intelligence_pass"),
            "database": os.getenv("DB_NAME", "intelligence"),
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", "5432"))
        }
    
    async def create_knowledge_document_from_scraped(
        self,
        scraped_data: Dict[str, Any],
        url: str,
        user_id: str = None,
        company_id: int = None
    ) -> uuid.UUID:
        try:
            conn = await asyncpg.connect(**self.db_config)
            
            try:
                doc_id = uuid.uuid4()
                title = scraped_data.get("title", "Contenuto Web Scrappato")
                content_text = scraped_data.get("content", "")
                content_hash = hashlib.md5(content_text.encode()).hexdigest()
                
                metadata = {
                    "source": "web_scraping",
                    "source_url": url,
                    "scraped_at": datetime.utcnow().isoformat(),
                    "extraction_method": scraped_data.get("extraction_method", "unknown")
                }
                
                # User UUID handling
                user_uuid = None
                if user_id:
                    try:
                        if len(user_id) == 36 and user_id.count('-') == 4:
                            user_uuid = uuid.UUID(user_id)
                    except:
                        user_uuid = None
                
                # Insert knowledge document
                insert_query = """
                INSERT INTO knowledge_documents (
                    id, filename, content_type, file_size, content_hash,
                    extracted_text, metadata, processed_at, company_id, uploaded_by
                ) VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb, $8, $9, $10)
                """
                
                await conn.execute(
                    insert_query,
                    doc_id,
                    f"scraped_{url.split('/')[-1] if url.split('/')[-1] else 'website'}.html",
                    "text/html",
                    len(content_text.encode()),
                    content_hash,
                    content_text,
                    json.dumps(metadata),
                    datetime.utcnow(),
                    company_id,
                    user_uuid
                )
                
                logger.info(f"✅ Knowledge document creato: {doc_id}")
                
                # Crea chunks con nome colonna corretto
                chunks_created = await self._create_document_chunks_correct(conn, doc_id, content_text)
                logger.info(f"✅ Creati {chunks_created} chunks per documento {doc_id}")
                
                return doc_id
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"❌ Errore creazione knowledge document: {str(e)}")
            raise Exception(f"Errore knowledge base integration: {str(e)}")
    
    async def _create_document_chunks_correct(self, conn, document_id: uuid.UUID, content_text: str):
        """Crea chunks con nome colonna corretto: content_chunk"""
        try:
            chunks = []
            chunk_size = 1000
            overlap = 200
            
            for i in range(0, len(content_text), chunk_size - overlap):
                chunk_text = content_text[i:i + chunk_size]
                if len(chunk_text.strip()) < 50:
                    continue
                    
                chunk_id = uuid.uuid4()
                chunks.append({
                    "id": chunk_id,
                    "document_id": document_id,
                    "chunk_index": len(chunks),
                    "content_chunk": chunk_text.strip()  # Nome corretto della colonna
                })
            
            # Insert chunks con schema corretto
            for chunk in chunks:
                insert_chunk_query = """
                INSERT INTO document_chunks (
                    id, document_id, chunk_index, content_chunk, created_at
                ) VALUES ($1, $2, $3, $4, $5)
                """
                
                await conn.execute(
                    insert_chunk_query,
                    chunk["id"],
                    chunk["document_id"],
                    chunk["chunk_index"],
                    chunk["content_chunk"],  # Usa content_chunk invece di content
                    datetime.utcnow()
                )
            
            return len(chunks)
            
        except Exception as e:
            logger.error(f"❌ Errore creazione chunks: {str(e)}")
            return 0
    
    async def get_knowledge_document_stats(self) -> Dict[str, Any]:
        try:
            conn = await asyncpg.connect(**self.db_config)
            
            try:
                total_docs = await conn.fetchval("SELECT COUNT(*) FROM knowledge_documents")
                scraped_docs = await conn.fetchval("SELECT COUNT(*) FROM knowledge_documents WHERE metadata->>'source' = 'web_scraping'")
                total_chunks = await conn.fetchval("SELECT COUNT(*) FROM document_chunks")
                
                return {
                    "total_documents": total_docs,
                    "scraped_documents": scraped_docs,
                    "total_chunks": total_chunks,
                    "last_update": datetime.utcnow().isoformat()
                }
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"❌ Errore getting stats: {str(e)}")
            return {"error": str(e), "last_update": datetime.utcnow().isoformat()}

# Istanza globale
kb_integration_fixed = KnowledgeBaseIntegrationChunksFixed()
