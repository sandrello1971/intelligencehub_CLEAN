#!/usr/bin/env python3
"""
Vettorizza file HTML con CONTENUTO nel payload
"""
import asyncio
import sys
import os
import hashlib
from pathlib import Path

sys.path.append('/var/www/intelligence/backend')

from app.modules.rag_engine.vector_service import VectorRAGService
import psycopg2

async def vectorize_html_with_content():
    """Vettorizza HTML con contenuto nel payload"""
    vector_service = VectorRAGService()
    
    print("🚀 Ri-vettorizzazione HTML con contenuto...")
    
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
            # Clean content
            import re
            clean_content = re.sub(r'<[^>]+>', '', content)  # Remove HTML tags
            clean_content = re.sub(r'\s+', ' ', clean_content).strip()  # Clean whitespace
            
            if len(clean_content) < 50:
                print(f"⚠️ Clean content too short: {filename}")
                continue
            
            # Create chunks WITH content
            chunk_size = 1000
            for i in range(0, len(clean_content), chunk_size):
                chunk_text = clean_content[i:i + chunk_size]
                
                point_id = int.from_bytes(
                    hashlib.md5(f"{filename}_{i//chunk_size}".encode()).digest()[:8], 
                    byteorder='big'
                ) % (2**31 - 1)
                
                try:
                    embedding = await vector_service.generate_embeddings(chunk_text)
                    
                    from qdrant_client.models import PointStruct
                    point = PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload={
                            'filename': filename,
                            'chunk_index': i // chunk_size,
                            'source': 'web_scraping',
                            'document_id': filename.replace('.html', ''),
                            'content': chunk_text  # ← CONTENUTO INCLUSO!
                        }
                    )
                    
                    vector_service.qdrant_client.upsert(
                        collection_name=vector_service.collection_name,
                        points=[point]
                    )
                    print(f"✅ Added chunk {i//chunk_size} for {filename}")
                    
                except Exception as e:
                    print(f"❌ Error adding chunk: {e}")
            
            successful += 1
            
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
    
    conn.close()
    
    print(f"\n📊 RISULTATI:")
    print(f"✅ Files successful: {successful}")
    
    try:
        stats = vector_service.get_stats()
        print(f"📈 Total points in Qdrant: {stats['total_points']}")
    except Exception as e:
        print(f"⚠️ Error getting stats: {e}")

if __name__ == "__main__":
    asyncio.run(vectorize_html_with_content())
