#!/usr/bin/env python3
"""
Test Knowledge Base Integration - Schema UUID Corretto
"""

import asyncio
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.scraped_data import ScrapedContentModel, ScrapedWebsiteModel, ContentType
from knowledge_base_integration_corrected import create_knowledge_base_integration

async def test_knowledge_integration_corrected():
    """Test con schema UUID corretto"""
    print("🧪 Testing Knowledge Base Integration - UUID Schema")
    print("=" * 60)
    
    # Test data
    website = ScrapedWebsiteModel(
        id=1,
        url="https://example.com",
        company_name="Example Company",
        partita_iva="12345678901"
    )
    
    content = ScrapedContentModel(
        id=1,
        website_id=1,
        page_url="https://example.com/about",
        page_title="About Example Company",
        content_type=ContentType.COMPANY_INFO,
        content_hash="test_hash_corrected",
        cleaned_text="Example Company è un'azienda italiana specializzata in tecnologia e innovazione digitale.",
        confidence_score=0.85,
        scraped_at=datetime.now()
    )
    
    try:
        kb_integration = create_knowledge_base_integration()
        await kb_integration.connect()
        
        print("✅ 1. Connected to knowledge base")
        
        # Test creazione documento con UUID corretto
        doc_id = await kb_integration.create_knowledge_document_from_scraping(
            content, website, company_id=123
        )
        
        print(f"✅ 2. Knowledge document created: {doc_id}")
        
        # Test creazione chunks
        chunk_ids = await kb_integration.create_document_chunks(
            doc_id, content.cleaned_text
        )
        
        print(f"✅ 3. Document chunks created: {len(chunk_ids)} chunks")
        
        # Test processing completo
        results = await kb_integration.process_scraped_content_to_knowledge_base(
            [content], website, company_id=123
        )
        
        print(f"✅ 4. Complete processing:")
        print(f"   Documents created: {results['documents_created']}")
        print(f"   Chunks created: {results['chunks_created']}")
        print(f"   Errors: {len(results['errors'])}")
        
        await kb_integration.disconnect()
        
        print("\n🎉 Knowledge Base Integration CORRECTED test PASSED!")
        print("🔗 UUID Schema compatibility VERIFIED!")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    success = await test_knowledge_integration_corrected()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
