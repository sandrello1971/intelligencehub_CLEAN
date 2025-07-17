#!/usr/bin/env python3
"""
Vettorizza file HTML dal database knowledge_documents
"""
import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append('/var/www/intelligence/backend')

from app.modules.rag_engine.vector_service import VectorRAGService
import psycopg2

async def vectorize_html_files():
    """Vettorizza file HTML da knowledge_documents"""
    vector_service = VectorRAGService()
    
    print("🚀 Vettorizzazione file HTML dal database...")
    
    # Connessione database
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "intelligence"),
        user=os.getenv("DB_USER", "intelligence_user"),
        password=os.getenv("DB_PASSWORD", "intelligence_pass"),
        port=int(os.getenv("DB_PORT", "5432"))
    )
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT filename, extracted_text 
        FROM knowledge_documents 
        WHERE filename LIKE 'scraped_%'
    """)
    
    successful = 0
    
    for row in cursor.fetchall():
        filename, content = row
        print(f"📄 Processing: {filename}")
        
        if not content or len(content.strip()) < 50:
            print(f"⚠️ Content too short: {filename}")
            continue
        
        try:
            # Create chunks
            chunks = []
            chunk_size = 1000
            for i in range(0, len(content), chunk_size):
                chunk_text = content[i:i + chunk_size]
                
                import hashlib
                point_id = int.from_bytes(
                    hashlib.md5(f"{filename}_{i//chunk_size}".encode()).digest()[:8], 
                    byteorder='big'
                ) % (2**31 - 1)
                
                chunks.append({
                    'id': point_id,
                    'text': chunk_text,
                    'metadata': {
                        'filename': filename,
                        'chunk_index': i // chunk_size,
                        'source': 'web_scraping',
                        'document_id': filename.replace('.html', '')
                    }
                })
            
            # Add chunks to Qdrant
            doc_successful = 0
            for chunk in chunks:
                try:
                    embedding = await vector_service.generate_embeddings(chunk['text'])
                    
                    from qdrant_client.models import PointStruct
                    point = PointStruct(
                        id=chunk['id'],
                        vector=embedding,
                        payload={**chunk["metadata"], "content": chunk["text"], "filename": filename}
                    )
                    
                    vector_service.qdrant_client.upsert(
                        collection_name=vector_service.collection_name,
                        points=[point]
                    )
                    doc_successful += 1
                    
                except Exception as e:
                    print(f"❌ Error adding chunk: {e}")
            
            if doc_successful > 0:
                print(f"✅ Vectorized: {filename} ({doc_successful} chunks)")
                successful += 1
            
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
    
    conn.close()
    
    print(f"\n📊 RISULTATI HTML:")
    print(f"✅ Files successful: {successful}")
    
    # Get final stats
    try:
        stats = vector_service.get_stats()
        print(f"📈 Total points in Qdrant: {stats['total_points']}")
    except Exception as e:
        print(f"⚠️ Error getting stats: {e}")

if __name__ == "__main__":
    asyncio.run(vectorize_html_files())
