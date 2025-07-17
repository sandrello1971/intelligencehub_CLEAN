"""
Knowledge Base Integration REALE - Intelligence Platform
Usa le tabelle esistenti: knowledge_documents, document_chunks
"""
import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
import hashlib
import asyncio

logger = logging.getLogger(__name__)

class RealKnowledgeIntegration:
    def __init__(self):
        self.initialized = False
        self._initialize()
    
    def _initialize(self):
        """Inizializzazione sicura con database reale"""
        try:
            # Import sicuro del database
            import asyncpg
            self.db_available = True
            self.initialized = True
            logger.info("✅ RealKnowledgeIntegration inizializzato")
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione KB real: {e}")
            self.initialized = False
    
    async def get_db_connection(self):
        """Connessione database sicura"""
        try:
            import asyncpg
            # Usa le stesse credenziali del sistema esistente
            conn = await asyncpg.connect(
                host="localhost",
                database="intelligence",
                user="intelligence_user", 
                password="intelligence_pass"
            )
            return conn
        except Exception as e:
            logger.error(f"❌ Errore connessione DB: {e}")
            return None
    
    async def create_knowledge_document(self, scraped_data: Dict[str, Any], user_id: str = "web-scraping") -> Optional[str]:
        """Crea documento REALE nella knowledge base"""
        if not self.initialized:
            logger.warning("⚠️ Knowledge integration non inizializzata")
            return None
        
        conn = None
        try:
            conn = await self.get_db_connection()
            if not conn:
                return None
            
            # Prepare document data
            content = scraped_data.get("content", "")
            url = scraped_data.get("url", "")
            title = scraped_data.get("title", f"Documento da {url}")
            
            # Generate content hash
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            doc_id = str(uuid.uuid4())
            
            # Metadata per web scraping
            metadata = {
                "source": "web_scraping",
                "url": url,
                "scraped_at": scraped_data.get("scraped_at", datetime.utcnow().isoformat()),
                "title": title,
                "content_length": len(content),
                "scraping_engine": "safe_engine_v1.0"
            }
            
            # SQL Insert sicuro
            insert_query = """
                INSERT INTO knowledge_documents 
                (id, filename, content_type, file_size, content_hash, extracted_text, metadata, uploaded_by, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                RETURNING id
            """
            
            current_time = datetime.utcnow()
            
            result = await conn.fetchrow(
                insert_query,
                doc_id,                                    # id
                f"scraped_{url.split('/')[-1] or 'document'}.html",  # filename
                "text/html",                              # content_type
                len(content.encode('utf-8')),             # file_size
                content_hash,                             # content_hash
                content,                                  # extracted_text
                metadata,                                 # metadata (jsonb)
                user_id,                                  # uploaded_by
                current_time,                             # created_at
                current_time                              # updated_at
            )
            
            if result:
                logger.info(f"✅ Knowledge document REALE creato: {doc_id}")
                logger.info(f"   - URL: {url}")
                logger.info(f"   - Content: {len(content)} caratteri")
                logger.info(f"   - Hash: {content_hash[:8]}...")
                return doc_id
            else:
                logger.error("❌ Insert fallito")
                return None
            
        except Exception as e:
            logger.error(f"❌ Errore creazione knowledge document REALE: {e}")
            return None
        finally:
            if conn:
                await conn.close()
    
    async def create_document_chunks(self, doc_id: str, content: str) -> int:
        """Crea chunks REALI per RAG"""
        conn = None
        try:
            conn = await self.get_db_connection()
            if not conn:
                return 0
            
            # Chunk creation logic REALE
            chunk_size = 1000
            overlap = 100
            chunks = []
            
            for i in range(0, len(content), chunk_size - overlap):
                chunk_text = content[i:i + chunk_size]
                if chunk_text.strip():  # Solo chunks non vuoti
                    chunks.append({
                        "text": chunk_text,
                        "start_pos": i,
                        "end_pos": min(i + chunk_size, len(content))
                    })
            
            # Insert chunks nel database
            chunks_inserted = 0
            for idx, chunk in enumerate(chunks):
                try:
                    insert_query = """
                        INSERT INTO document_chunks 
                        (id, document_id, chunk_index, content, metadata, created_at)
                        VALUES ($1, $2, $3, $4, $5, $6)
                    """
                    
                    chunk_metadata = {
                        "start_position": chunk["start_pos"],
                        "end_position": chunk["end_pos"],
                        "chunk_size": len(chunk["text"]),
                        "source": "web_scraping_chunker"
                    }
                    
                    await conn.execute(
                        insert_query,
                        str(uuid.uuid4()),           # chunk id
                        doc_id,                      # document_id
                        idx,                         # chunk_index
                        chunk["text"],               # content
                        chunk_metadata,              # metadata
                        datetime.utcnow()           # created_at
                    )
                    chunks_inserted += 1
                    
                except Exception as e:
                    logger.error(f"❌ Errore insert chunk {idx}: {e}")
            
            logger.info(f"✅ Creati {chunks_inserted} chunks REALI per documento {doc_id}")
            return chunks_inserted
            
        except Exception as e:
            logger.error(f"❌ Errore creazione chunks REALI: {e}")
            return 0
        finally:
            if conn:
                await conn.close()
    
    async def get_stats(self) -> Dict[str, Any]:
        """Statistiche REALI knowledge base"""
        conn = None
        try:
            conn = await self.get_db_connection()
            if not conn:
                return {"error": "Database connection failed"}
            
            # Query statistiche reali
            stats_query = """
                SELECT 
                    COUNT(*) as total_documents,
                    COUNT(CASE WHEN metadata->>'source' = 'web_scraping' THEN 1 END) as scraped_documents,
                    MAX(updated_at) as last_update
                FROM knowledge_documents
            """
            
            chunks_query = """
                SELECT COUNT(*) as total_chunks
                FROM document_chunks
            """
            
            stats_result = await conn.fetchrow(stats_query)
            chunks_result = await conn.fetchrow(chunks_query)
            
            return {
                "total_documents": stats_result["total_documents"] if stats_result else 0,
                "scraped_documents": stats_result["scraped_documents"] if stats_result else 0,
                "total_chunks": chunks_result["total_chunks"] if chunks_result else 0,
                "last_update": stats_result["last_update"].isoformat() if stats_result and stats_result["last_update"] else None,
                "integration_status": "real_database",
                "database_type": "postgresql"
            }
            
        except Exception as e:
            logger.error(f"❌ Errore getting stats REALI: {e}")
            return {
                "error": str(e),
                "integration_status": "error",
                "last_update": datetime.utcnow().isoformat()
            }
        finally:
            if conn:
                await conn.close()

# Istanza globale REALE
real_kb_integration = RealKnowledgeIntegration()
