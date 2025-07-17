#!/usr/bin/env python3
"""
Test RAG Integration Semplificato
"""

import asyncio
import sys
import os
from datetime import datetime

# Import locale
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rag_integration_simple import SimpleRAGIntegration

async def test_simple_rag():
    """Test RAG integration semplificato"""
    print("🧪 Testing Simple RAG Integration...")
    
    # Contenuto test semplificato
    test_content = {
        'id': 1,
        'page_url': 'https://example.com/about',
        'page_title': 'About Example Company',
        'content_type': 'company_info',
        'cleaned_text': 'Example Company è un\'azienda leader nel settore tecnologico italiano. Fondata nel 2020, la società si occupa di sviluppo software e consulenza AI.',
        'confidence_score': 0.85,
        'scraped_at': datetime.now().isoformat()
    }
    
    try:
        # Test RAG integration
        rag = SimpleRAGIntegration()
        result = await rag.process_content_for_rag(test_content)
        
        print(f"✅ RAG processing completed!")
        print(f"   Content ID: {result['content_id']}")
        print(f"   Status: {result['processing_status']}")
        print(f"   Document ID: {result['knowledge_document_id']}")
        print(f"   Chunks: {result['chunks_created']}")
        print(f"   Embeddings: {result['embeddings_created']}")
        print(f"   Errors: {len(result['errors'])}")
        
        # Statistiche
        stats = rag.get_stats()
        print(f"   Stats: {stats}")
        
        return result['processing_status'] == 'completed'
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def main():
    """Main test"""
    print("🚀 Testing Simple RAG Integration")
    print("=" * 50)
    
    success = await test_simple_rag()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Simple RAG test passed!")
    else:
        print("❌ Simple RAG test failed!")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
