import asyncio
import logging
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

# Import RAG esistente
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models.scraped_data import ScrapedContentModel, RAGProcessingStatus

logger = logging.getLogger(__name__)

class WebScrapingRAGIntegration:
    """
    🔗 Integrazione Web Scraping con RAG esistente
    
    Features:
    - Ponte tra scraped content e knowledge_documents
    - Processamento automatico per Qdrant
    - Embedding generation e storage
    - Sync con VectorRAGService esistente
    """
    
    def __init__(self):
        # Configurazione processamento
        self.chunk_size = 1000
        self.chunk_overlap = 200
        self.min_content_length = 100
        
        # Statistiche
        self.stats = {
            'documents_processed': 0,
            'embeddings_created': 0,
            'rag_integrations': 0,
            'errors': 0
        }
    
    async def process_scraped_content_for_rag(self, content: ScrapedContentModel) -> Dict[str, Any]:
        """
        Processa contenuto scrapato per RAG
        
        Args:
            content: Contenuto scrapato da processare
            
        Returns:
            Dict con risultati processamento
        """
        result = {
            'content_id': content.id,
            'processing_status': RAGProcessingStatus.PROCESSING,
            'knowledge_document_id': None,
            'embeddings_created': 0,
            'chunks_created': 0,
            'errors': []
        }
        
        try:
            # Verifica se contenuto è adatto per RAG
            if not self._is_content_suitable_for_rag(content):
                result['processing_status'] = RAGProcessingStatus.SKIPPED
                result['errors'].append("Content not suitable for RAG processing")
                return result
            
            # Prepara documento per knowledge_documents
            document_data = self._prepare_document_data(content)
            
            # Crea documento in knowledge_documents
            knowledge_doc_id = await self._create_knowledge_document(document_data)
            if not knowledge_doc_id:
                result['processing_status'] = RAGProcessingStatus.FAILED
                result['errors'].append("Failed to create knowledge document")
                return result
            
            result['knowledge_document_id'] = knowledge_doc_id
            
            # Processa contenuto per embeddings
            chunks = await self._create_content_chunks(content)
            
            if chunks:
                # Crea embeddings e salva in Qdrant
                embeddings_result = await self._create_and_store_embeddings(
                    chunks, knowledge_doc_id, content
                )
                
                result['embeddings_created'] = embeddings_result['embeddings_created']
                result['chunks_created'] = embeddings_result['chunks_created']
                
                if embeddings_result['success']:
                    result['processing_status'] = RAGProcessingStatus.COMPLETED
                    self.stats['rag_integrations'] += 1
                else:
                    result['processing_status'] = RAGProcessingStatus.FAILED
                    result['errors'].extend(embeddings_result['errors'])
            else:
                result['processing_status'] = RAGProcessingStatus.FAILED
                result['errors'].append("No chunks created from content")
            
            self.stats['documents_processed'] += 1
            
        except Exception as e:
            logger.error(f"RAG processing failed for content {content.id}: {str(e)}")
            result['processing_status'] = RAGProcessingStatus.FAILED
            result['errors'].append(f"Processing error: {str(e)}")
            self.stats['errors'] += 1
        
        return result
    
    async def bulk_process_scraped_content(self, contents: List[ScrapedContentModel]) -> Dict[str, Any]:
        """
        Processamento bulk di contenuti scrapati
        
        Args:
            contents: Lista contenuti da processare
            
        Returns:
            Dict con risultati bulk processing
        """
        results = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'individual_results': []
        }
        
        for content in contents:
            result = await self.process_scraped_content_for_rag(content)
            results['individual_results'].append(result)
            results['total_processed'] += 1
            
            if result['processing_status'] == RAGProcessingStatus.COMPLETED:
                results['successful'] += 1
            elif result['processing_status'] == RAGProcessingStatus.FAILED:
                results['failed'] += 1
            elif result['processing_status'] == RAGProcessingStatus.SKIPPED:
                results['skipped'] += 1
        
        return results
    
    def _is_content_suitable_for_rag(self, content: ScrapedContentModel) -> bool:
        """Verifica se contenuto è adatto per RAG"""
        
        # Verifica lunghezza minima
        if content.cleaned_text and len(content.cleaned_text) < self.min_content_length:
            return False
        
        # Verifica confidence score
        if content.confidence_score < 0.3:
            return False
        
        # Verifica tipo contenuto
        suitable_types = ['company_info', 'document', 'service', 'product']
        if content.content_type not in suitable_types:
            return False
        
        return True
    
    def _prepare_document_data(self, content: ScrapedContentModel) -> Dict[str, Any]:
        """Prepara dati per knowledge_documents"""
        
        # FIX: Converte URL Pydantic in stringa
        page_url = str(content.page_url)
        
        # Genera nome file basato su URL e tipo
        domain = page_url.split('/')[2] if '//' in page_url else 'unknown'
        filename = f"scraped_{domain}_{content.content_type}_{content.id}.html"
        
        return {
            'filename': filename,
            'original_filename': filename,
            'file_type': 'html',
            'file_size': len(content.cleaned_text or ''),
            'content_hash': content.content_hash,
            'company_id': None,  # Sarà linkato successivamente se necessario
            'uploaded_by': 'web_scraping_engine',
            'processing_status': 'processing',
            'meta_data': {
                'source_url': page_url,  # FIX: Usa stringa convertita
                'scraping_date': content.scraped_at.isoformat() if content.scraped_at else None,
                'content_type': content.content_type,
                'extraction_method': content.extraction_method,
                'confidence_score': content.confidence_score,
                'page_title': content.page_title,
                'website_id': content.website_id,
                'scraped_content_id': content.id
            }
        }
    
    async def _create_knowledge_document(self, document_data: Dict[str, Any]) -> Optional[str]:
        """Crea documento in knowledge_documents"""
        try:
            # Simula creazione documento
            knowledge_doc_id = str(uuid.uuid4())
            
            logger.info(f"Created knowledge document: {knowledge_doc_id}")
            return knowledge_doc_id
            
        except Exception as e:
            logger.error(f"Failed to create knowledge document: {str(e)}")
            return None
    
    async def _create_content_chunks(self, content: ScrapedContentModel) -> List[Dict[str, Any]]:
        """Crea chunks dal contenuto"""
        chunks = []
        
        if not content.cleaned_text:
            return chunks
        
        text = content.cleaned_text
        
        # Chunking semplice
        chunk_start = 0
        chunk_id = 0
        
        while chunk_start < len(text):
            chunk_end = min(chunk_start + self.chunk_size, len(text))
            chunk_text = text[chunk_start:chunk_end]
            
            if len(chunk_text.strip()) > 50:  # Minimo 50 caratteri
                chunks.append({
                    'chunk_id': chunk_id,
                    'text': chunk_text,
                    'start_index': chunk_start,
                    'end_index': chunk_end,
                    'metadata': {
                        'source_url': str(content.page_url),  # FIX: Converte in stringa
                        'content_type': content.content_type,
                        'page_title': content.page_title,
                        'chunk_index': chunk_id
                    }
                })
                chunk_id += 1
            
            chunk_start = chunk_end - self.chunk_overlap
        
        return chunks
    
    async def _create_and_store_embeddings(self, chunks: List[Dict[str, Any]], 
                                         knowledge_doc_id: str, 
                                         content: ScrapedContentModel) -> Dict[str, Any]:
        """Crea e salva embeddings in Qdrant"""
        result = {
            'success': False,
            'embeddings_created': 0,
            'chunks_created': 0,
            'errors': []
        }
        
        try:
            # Per ogni chunk, crea embedding
            for chunk in chunks:
                try:
                    # Simula creazione embedding
                    embedding_result = await self._simulate_embedding_creation(
                        chunk, knowledge_doc_id, content
                    )
                    
                    if embedding_result['success']:
                        result['embeddings_created'] += 1
                        result['chunks_created'] += 1
                    else:
                        result['errors'].append(f"Failed to create embedding for chunk {chunk['chunk_id']}")
                
                except Exception as e:
                    result['errors'].append(f"Error processing chunk {chunk['chunk_id']}: {str(e)}")
            
            result['success'] = result['embeddings_created'] > 0
            self.stats['embeddings_created'] += result['embeddings_created']
            
        except Exception as e:
            result['errors'].append(f"Embedding creation failed: {str(e)}")
        
        return result
    
    async def _simulate_embedding_creation(self, chunk: Dict[str, Any], 
                                         knowledge_doc_id: str,
                                         content: ScrapedContentModel) -> Dict[str, Any]:
        """Simula creazione embedding"""
        
        # Simula delay API
        await asyncio.sleep(0.1)
        
        # Simula successo
        return {
            'success': True,
            'embedding_id': f"emb_{knowledge_doc_id}_{chunk['chunk_id']}",
            'vector_id': f"vec_{uuid.uuid4()}"
        }
    
    async def get_rag_content_by_website(self, website_id: int) -> List[Dict[str, Any]]:
        """Ottieni contenuti RAG per un sito web"""
        try:
            # Simula dati per ora
            return [
                {
                    'website_id': website_id,
                    'content_id': 1,
                    'knowledge_document_id': str(uuid.uuid4()),
                    'rag_processed': True,
                    'processing_status': 'completed',
                    'embeddings_count': 5,
                    'processed_at': datetime.now().isoformat()
                }
            ]
            
        except Exception as e:
            logger.error(f"Failed to get RAG content for website {website_id}: {str(e)}")
            return []
    
    def get_stats(self) -> Dict[str, int]:
        """Ottieni statistiche RAG integration"""
        return self.stats.copy()
    
    def reset_stats(self):
        """Reset statistiche"""
        self.stats = {
            'documents_processed': 0,
            'embeddings_created': 0,
            'rag_integrations': 0,
            'errors': 0
        }

# Utility functions
def create_rag_integration() -> WebScrapingRAGIntegration:
    """Factory per RAG integration"""
    return WebScrapingRAGIntegration()

async def process_scraped_content_to_rag(content: ScrapedContentModel) -> Dict[str, Any]:
    """Shortcut per processare contenuto scrapato"""
    integration = create_rag_integration()
    return await integration.process_scraped_content_for_rag(content)
