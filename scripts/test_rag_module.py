#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.append('/var/www/intelligence/backend')

from app.modules.rag_engine import VectorRAGService, DocumentProcessor, KnowledgeManager

async def test_rag_module():
    print("🧪 Testing RAG Module...")
    
    # Test Vector Service
    try:
        vector_service = VectorRAGService()
        health = vector_service.health_check()
        print(f"✅ Vector Service Health: {health}")
    except Exception as e:
        print(f"❌ Vector Service failed: {e}")
        return False
    
    # Test Document Processor
    try:
        processor = DocumentProcessor()
        formats = processor.get_supported_formats()
        print(f"✅ Document Processor - Formats: {formats}")
    except Exception as e:
        print(f"❌ Document Processor failed: {e}")
        return False
    
    # Test Knowledge Manager
    try:
        knowledge_manager = KnowledgeManager()
        health = await knowledge_manager.health_check()
        print(f"✅ Knowledge Manager Health: {health}")
    except Exception as e:
        print(f"❌ Knowledge Manager failed: {e}")
        return False
    
    print("🎉 All RAG module tests passed!")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_rag_module())
    sys.exit(0 if success else 1)
