#!/usr/bin/env python3
"""
Script per vettorizzare documenti esistenti in Qdrant - FIXED VERSION
"""
import asyncio
import sys
import os
import hashlib
from pathlib import Path

# Add backend to path
sys.path.append('/var/www/intelligence/backend')

from app.modules.rag_engine.vector_service import VectorRAGService
from app.modules.rag_engine.document_processor import DocumentProcessor

def generate_point_id(document_id: str, chunk_index: int) -> int:
    """Genera un ID numerico valido per Qdrant"""
    # Crea hash del document_id + chunk_index
    combined = f"{document_id}_{chunk_index}"
    hash_obj = hashlib.md5(combined.encode())
    # Prendi i primi 8 bytes e convertili in int
    return int.from_bytes(hash_obj.digest()[:8], byteorder='big') % (2**31 - 1)

async def vectorize_existing_documents():
    """Vettorizza tutti i documenti esistenti con ID numerici validi"""
    upload_dir = Path("/var/www/intelligence/backend/uploads")
    vector_service = VectorRAGService()
    doc_processor = DocumentProcessor()
    
    print("🚀 Avvio vettorizzazione documenti esistenti...")
    
    # Get all documents
    documents = list(upload_dir.glob("*.txt")) + list(upload_dir.glob("*.pdf")) + list(upload_dir.glob("*.docx"))
    print(f"📁 Trovati {len(documents)} documenti")
    
    successful = 0
    failed = 0
    total_chunks = 0
    
    for doc_path in documents:
        try:
            print(f"📄 Processing: {doc_path.name}")
            
            # Extract text
            extraction_result = await doc_processor.extract_text(doc_path)
            if not extraction_result['success']:
                print(f"❌ Extraction failed: {doc_path.name}")
                failed += 1
                continue
            
            text = extraction_result['text']
            if len(text.strip()) < 50:
                print(f"⚠️ Text too short: {doc_path.name}")
                continue
            
            # Create chunks con ID numerici
            chunks = []
            chunk_size = 1000
            for i in range(0, len(text), chunk_size):
                chunk_text = text[i:i + chunk_size]
                # ID numerico valido per Qdrant
                point_id = generate_point_id(doc_path.stem, i // chunk_size)
                
                chunks.append({
                    'id': point_id,
                    'text': chunk_text,
                    'metadata': {
                        'filename': doc_path.name,
                        'chunk_index': i // chunk_size,
                        'source': 'existing_upload',
                        'document_id': doc_path.stem
                    }
                })
            
            # Add chunks singolarmente per debug migliore
            doc_successful = 0
            for chunk in chunks:
                try:
                    # Genera embeddings
                    embedding = await vector_service.generate_embeddings(chunk['text'])
                    
                    # Crea point per Qdrant
                    from qdrant_client.models import PointStruct
                    point = PointStruct(
                        id=chunk['id'],
                        vector=embedding,
                        payload=chunk['metadata']
                    )
                    
                    # Upsert singolo point
                    vector_service.qdrant_client.upsert(
                        collection_name=vector_service.collection_name,
                        points=[point]
                    )
                    doc_successful += 1
                    
                except Exception as e:
                    print(f"❌ Error adding chunk {chunk['id']}: {e}")
            
            if doc_successful > 0:
                print(f"✅ Vectorized: {doc_path.name} ({doc_successful} chunks)")
                successful += 1
                total_chunks += doc_successful
            else:
                print(f"❌ Failed vectorization: {doc_path.name}")
                failed += 1
                
        except Exception as e:
            print(f"❌ Error processing {doc_path.name}: {e}")
            failed += 1
    
    print(f"\n📊 RISULTATI:")
    print(f"✅ Documents successful: {successful}")
    print(f"❌ Documents failed: {failed}")
    print(f"📈 Total chunks added: {total_chunks}")
    
    # Get final stats
    try:
        stats = vector_service.get_stats()
        print(f"📈 Total points in Qdrant: {stats['total_points']}")
    except Exception as e:
        print(f"⚠️ Error getting stats: {e}")

if __name__ == "__main__":
    asyncio.run(vectorize_existing_documents())
