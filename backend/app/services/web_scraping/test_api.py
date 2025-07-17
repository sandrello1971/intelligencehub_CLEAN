#!/usr/bin/env python3
"""
Test API Routes
"""

import asyncio
import sys
import os
from datetime import datetime
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock FastAPI per test
class MockRequest:
    pass

class MockHTTPException(Exception):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail

# Mock modules
sys.modules['fastapi'] = type('MockFastAPI', (), {
    'APIRouter': lambda **kwargs: type('Router', (), {})(),
    'HTTPException': MockHTTPException,
    'Depends': lambda x: x,
    'BackgroundTasks': type('BackgroundTasks', (), {})
})()

from api_routes import *

async def test_health_endpoint():
    """Test health check"""
    print("🧪 Testing health endpoint...")
    
    try:
        result = await health_check()
        print(f"✅ Health check: {result['status']}")
        print(f"   Service: {result['service']}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

async def test_scrape_endpoint():
    """Test scrape website endpoint"""
    print("\n🧪 Testing scrape website endpoint...")
    
    try:
        website_data = {
            "url": "https://example.com",
            "company_name": "Test Company",
            "respect_robots_txt": True,
            "auto_rag_processing": True
        }
        
        result = await scrape_website(website_data)
        print(f"✅ Scraping completed: {result['success']}")
        
        if result.get('scraping_results'):
            scraping = result['scraping_results']
            print(f"   Pages scraped: {scraping.get('pages_scraped', 0)}")
            print(f"   Content extracted: {len(scraping.get('content_extracted', []))}")
        
        if result.get('rag_results'):
            print(f"   RAG processing: {len(result['rag_results'])} items")
        
        return True
    except Exception as e:
        print(f"❌ Scraping test failed: {e}")
        return False

async def test_stats_endpoint():
    """Test stats endpoint"""
    print("\n🧪 Testing stats endpoint...")
    
    try:
        result = await get_scraping_stats()
        print(f"✅ Stats retrieved: {result['success']}")
        print(f"   RAG stats: {result['rag_stats']}")
        print(f"   DB stats: {result['database_stats']}")
        return True
    except Exception as e:
        print(f"❌ Stats test failed: {e}")
        return False

async def test_content_types_endpoint():
    """Test content types endpoint"""
    print("\n🧪 Testing content types endpoint...")
    
    try:
        result = await get_content_types()
        print(f"✅ Content types: {len(result['content_types'])} types")
        print(f"   Frequencies: {len(result['scraping_frequencies'])} options")
        return True
    except Exception as e:
        print(f"❌ Content types test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Testing Web Scraping API Routes")
    print("=" * 60)
    
    tests = [
        test_health_endpoint,
        test_scrape_endpoint,
        test_stats_endpoint,
        test_content_types_endpoint
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if await test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 API Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All API tests passed!")
        return 0
    else:
        print("❌ Some API tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
