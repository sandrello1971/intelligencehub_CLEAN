"""
Knowledge Base Integration FIXED - Intelligence Platform
Fix per JSON serialization metadata
"""
import logging
import uuid
import json  # IMPORTANTE: Import json per serialization
from typing import Dict, Any, Optional
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

class FixedKnowledgeIntegration:
    def __init__(self):
        self.initialized = False
        self.web_scraping_user_id = "00000000-0000-0000-0000-000000000001"  # UUID fisso per web scraping
        self._initialize()
    
    def _initialize(self):
        """Inizializzazione sicura con UUID corretto"""
        try:
            import asyncpg
            self.db_available = True
            self.initialized = True
            logger.info("✅ FixedKnowledgeIntegration inizializzato")
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione KB fixed: {e}")
            self.initialized = False
    
    async def get_db_connection(self):
        """Connessione database sicura"""
        try:
            import asyncpg
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
        """Crea documento REALE con JSON serialization corretta"""
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
            
            # Generate IDs
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            doc_id = str(uuid.uuid4())
            
            # Fix: Converte user_id in UUID valido
            if user_id == "web-scraping" or user_id == "api-user":
                uploaded_by_uuid = self.web_scraping_user_id
            else:
                try:
                    # Verifica se è già un UUID valido
                    uuid.UUID(user_id)
                    uploaded_by_uuid = user_id
                except ValueError:
                    # Se non è UUID, usa quello fisso
                    uploaded_by_uuid = self.web_scraping_user_id
            
            # Metadata per web scraping
            metadata_dict = {
                "source": "web_scraping",
                "url": url,
                "scraped_at": scraped_data.get("scraped_at", datetime.utcnow().isoformat()),
                "title": title,
                "content_length": len(content),
                "scraping_engine": "safe_engine_v1.0"
            }
            
            # FIX CRITICO: Serializza metadata come JSON string
            metadata_json = json.dumps(metadata_dict)
            
            # SQL Insert con JSON string corretto
            insert_query = """
                INSERT INTO knowledge_documents 
                (id, filename, content_type, file_size, content_hash, extracted_text, metadata, uploaded_by, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb, $8::uuid, $9, $10)
                RETURNING id
            """
            
            current_time = datetime.utcnow()
            
            result = await conn.fetchrow(
                insert_query,
                doc_id,                                    # id
                f"scraped_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",  # filename
                "text/html",                              # content_type
                len(content.encode('utf-8')),             # file_size
                content_hash,                             # content_hash
                content,                                  # extracted_text
                metadata_json,                            # metadata (JSON STRING!)
                uploaded_by_uuid,                         # uploaded_by (UUID corretto!)
                current_time,                             # created_at
                current_time                              # updated_at
            )
            
            if result:
                logger.info(f"✅ Knowledge document JSON-FIXED creato: {doc_id}")
                logger.info(f"   - URL: {url}")
                logger.info(f"   - Content: {len(content)} caratteri")
                logger.info(f"   - Metadata JSON: {metadata_json[:100]}...")
                logger.info(f"   - Uploaded by: {uploaded_by_uuid}")
                logger.info(f"   - Hash: {content_hash[:8]}...")
                return doc_id
            else:
                logger.error("❌ Insert fallito")
                return None
            
        except Exception as e:
            logger.error(f"❌ Errore creazione knowledge document JSON-FIXED: {e}")
            logger.error(f"❌ Exception type: {type(e)}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return None
        finally:
            if conn:
                await conn.close()
    
    async def create_document_chunks(self, doc_id: str, content: str) -> int:
        """Crea chunks REALI per RAG con JSON corretto"""
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
                        (id, document_id, chunk_index, content_chunk, metadata, created_at)
                        VALUES ($1, $2, $3, $4, $5::jsonb, $6)
                    """
                    
                    chunk_metadata_dict = {
                        "start_position": chunk["start_pos"],
                        "end_position": chunk["end_pos"],
                        "chunk_size": len(chunk["text"]),
                        "source": "web_scraping_chunker"
                    }
                    
                    # FIX: JSON serialization anche per chunks
                    chunk_metadata_json = json.dumps(chunk_metadata_dict)
                    
                    await conn.execute(
                        insert_query,
                        str(uuid.uuid4()),           # chunk id
                        doc_id,                      # document_id (UUID string)
                        idx,                         # chunk_index
                        chunk["text"],               # content
                        chunk_metadata_json,         # metadata (JSON STRING!)
                        datetime.utcnow()           # created_at
                    )
                    chunks_inserted += 1
                    
                except Exception as e:
                    logger.error(f"❌ Errore insert chunk {idx}: {e}")
            
            logger.info(f"✅ Creati {chunks_inserted} chunks JSON-FIXED per documento {doc_id}")
            return chunks_inserted
            
        except Exception as e:
            logger.error(f"❌ Errore creazione chunks JSON-FIXED: {e}")
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
                "integration_status": "json_fixed_database",
                "database_type": "postgresql",
                "uuid_fix": "applied",
                "json_fix": "applied"
            }
            
        except Exception as e:
            logger.error(f"❌ Errore getting stats JSON-FIXED: {e}")
            return {
                "error": str(e),
                "integration_status": "error",
                "last_update": datetime.utcnow().isoformat()
            }
        finally:
            if conn:
                await conn.close()

# Istanza globale JSON-FIXED
fixed_kb_integration = FixedKnowledgeIntegration()
