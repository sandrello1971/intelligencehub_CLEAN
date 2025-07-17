#!/usr/bin/env python3
"""
Script per vettorizzare documenti esistenti in Qdrant
Migrazione da file scanning a vector search
"""
import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append('/var/www/intelligence/backend')

from app.modules.rag_engine.vector_service import VectorRAGService
from app.modules.rag_engine.document_processor import DocumentProcessor

async def vectorize_existing_documents():
    """Vettorizza tutti i documenti esistenti"""
    upload_dir = Path("/var/www/intelligence/backend/uploads")
    vector_service = VectorRAGService()
    doc_processor = DocumentProcessor()
    
    print("🚀 Avvio vettorizzazione documenti esistenti...")
    
    # Get all documents
    documents = list(upload_dir.glob("*.txt")) + list(upload_dir.glob("*.pdf")) + list(upload_dir.glob("*.docx"))
    print(f"📁 Trovati {len(documents)} documenti")
    
    successful = 0
    failed = 0
    
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
            
            # Create chunks
            chunks = []
            chunk_size = 1000
            for i in range(0, len(text), chunk_size):
                chunk_text = text[i:i + chunk_size]
                chunks.append({
                    'text': chunk_text,
                    'metadata': {
                        'filename': doc_path.name,
                        'chunk_index': i // chunk_size,
                        'source': 'existing_upload'
                    }
                })
            
            # Add to vector database
            document_id = doc_path.stem
            success = await vector_service.add_document_chunks(chunks, document_id)
            
            if success:
                print(f"✅ Vectorized: {doc_path.name} ({len(chunks)} chunks)")
                successful += 1
            else:
                print(f"❌ Failed vectorization: {doc_path.name}")
                failed += 1
                
        except Exception as e:
            print(f"❌ Error processing {doc_path.name}: {e}")
            failed += 1
    
    print(f"\n📊 RISULTATI:")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Total points in Qdrant: {vector_service.get_stats()['total_points']}")

if __name__ == "__main__":
    asyncio.run(vectorize_existing_documents())
#!/usr/bin/env python3
"""
Script per vettorizzare documenti esistenti in Qdrant
Migrazione da file scanning a vector search
"""
import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append('/var/www/intelligence/backend')

from app.modules.rag_engine.vector_service import VectorRAGService
from app.modules.rag_engine.document_processor import DocumentProcessor

async def vectorize_existing_documents():
    """Vettorizza tutti i documenti esistenti"""
    upload_dir = Path("/var/www/intelligence/backend/uploads")
    vector_service = VectorRAGService()
    doc_processor = DocumentProcessor()
    
    print("🚀 Avvio vettorizzazione documenti esistenti...")
    
    # Get all documents
    documents = list(upload_dir.glob("*.txt")) + list(upload_dir.glob("*.pdf")) + list(upload_dir.glob("*.docx"))
    print(f"📁 Trovati {len(documents)} documenti")
    
    successful = 0
    failed = 0
    
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
            
            # Create chunks
            chunks = []
            chunk_size = 1000
            for i in range(0, len(text), chunk_size):
                chunk_text = text[i:i + chunk_size]
                chunks.append({
                    'text': chunk_text,
                    'metadata': {
                        'filename': doc_path.name,
                        'chunk_index': i // chunk_size,
                        'source': 'existing_upload'
                    }
                })
            
            # Add to vector database
            document_id = doc_path.stem
            success = await vector_service.add_document_chunks(chunks, document_id)
            
            if success:
                print(f"✅ Vectorized: {doc_path.name} ({len(chunks)} chunks)")
                successful += 1
            else:
                print(f"❌ Failed vectorization: {doc_path.name}")
                failed += 1
                
        except Exception as e:
            print(f"❌ Error processing {doc_path.name}: {e}")
            failed += 1
    
    print(f"\n📊 RISULTATI:")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    
    # Get final stats
    try:
        stats = vector_service.get_stats()
        print(f"📈 Total points in Qdrant: {stats['total_points']}")
    except Exception as e:
        print(f"⚠️ Error getting stats: {e}")

if __name__ == "__main__":
    asyncio.run(vectorize_existing_documents())
