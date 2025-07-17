#!/usr/bin/env python3
"""
Test API Functions (senza FastAPI)
"""

import asyncio
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.scraped_data import ScrapedWebsiteModel
from scraping_engine import IntelligenceWebScrapingEngine
from rag_integration_simple import SimpleRAGIntegration

class WebScrapingAPI:
    """
    🌐 API Functions per Web Scraping
    (Versione semplificata per test)
    """
    
    def __init__(self):
        self.rag_integration = SimpleRAGIntegration()
    
    async def health_check(self):
        """Health check"""
        return {
            "status": "healthy", 
            "service": "intelligence-web-scraping",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat()
        }
    
    async def scrape_website(self, website_data: dict):
        """Scrape singolo website"""
        try:
            # Crea modello website
            website_model = ScrapedWebsiteModel(
                id=website_data.get('id', 1),
                url=website_data['url'],
                company_name=website_data.get('company_name'),
                respect_robots_txt=website_data.get('respect_robots_txt', True),
                scraping_frequency=website_data.get('scraping_frequency', 'on_demand')
            )
            
            # Esegui scraping
            async with IntelligenceWebScrapingEngine(rate_limit_delay=1.0) as engine:
                scraping_results = await engine.scrape_website(website_model)
            
            # RAG processing se richiesto
            rag_results = None
            auto_rag = website_data.get('auto_rag_processing', False)
            
            if auto_rag and scraping_results.get('content_extracted'):
                rag_results = []
                for content in scraping_results['content_extracted']:
                    content_dict = content.model_dump() if hasattr(content, 'model_dump') else content
                    rag_result = await self.rag_integration.process_content_for_rag(content_dict)
                    rag_results.append(rag_result)
            
            return {
                "success": True,
                "scraping_results": scraping_results,
                "rag_results": rag_results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_stats(self):
        """Ottieni statistiche"""
        try:
            rag_stats = self.rag_integration.get_stats()
            
            return {
                "success": True,
                "rag_stats": rag_stats,
                "database_stats": {
                    "websites_total": 0,
                    "content_total": 0,
                    "contacts_total": 0,
                    "companies_total": 0
                },
                "system_info": {
                    "service_version": "1.0.0",
                    "status": "operational",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_content_types(self):
        """Lista tipi contenuto supportati"""
        return {
            "success": True,
            "content_types": [
                {"value": "company_info", "label": "Company Information"},
                {"value": "contact_info", "label": "Contact Information"},
                {"value": "document", "label": "Document"},
                {"value": "news", "label": "News Article"},
                {"value": "product", "label": "Product Information"},
                {"value": "service", "label": "Service Information"},
                {"value": "general", "label": "General Content"}
            ],
            "scraping_frequencies": [
                {"value": "daily", "label": "Daily"},
                {"value": "weekly", "label": "Weekly"},
                {"value": "monthly", "label": "Monthly"},
                {"value": "on_demand", "label": "On Demand"}
            ],
            "timestamp": datetime.now().isoformat()
        }

async def test_health_endpoint():
    """Test health check"""
    print("🧪 Testing health endpoint...")
    
    try:
        api = WebScrapingAPI()
        result = await api.health_check()
        
        print(f"✅ Health check: {result['status']}")
        print(f"   Service: {result['service']}")
        print(f"   Version: {result['version']}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

async def test_scrape_endpoint():
    """Test scrape website endpoint"""
    print("\n🧪 Testing scrape website endpoint...")
    
    try:
        api = WebScrapingAPI()
        website_data = {
            "url": "https://example.com",
            "company_name": "Test Company",
            "respect_robots_txt": True,
            "auto_rag_processing": True
        }
        
        result = await api.scrape_website(website_data)
        
        print(f"✅ Scraping completed: {result['success']}")
        
        if result.get('scraping_results'):
            scraping = result['scraping_results']
            print(f"   Status: {scraping.get('status')}")
            print(f"   Pages scraped: {scraping.get('pages_scraped', 0)}")
            print(f"   Content extracted: {len(scraping.get('content_extracted', []))}")
            print(f"   Contacts found: {len(scraping.get('contacts_found', []))}")
            print(f"   Companies found: {len(scraping.get('companies_found', []))}")
        
        if result.get('rag_results'):
            rag_success = sum(1 for r in result['rag_results'] if r.get('processing_status') == 'completed')
            print(f"   RAG processing: {rag_success}/{len(result['rag_results'])} successful")
        
        return result['success']
        
    except Exception as e:
        print(f"❌ Scraping test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_stats_endpoint():
    """Test stats endpoint"""
    print("\n🧪 Testing stats endpoint...")
    
    try:
        api = WebScrapingAPI()
        result = await api.get_stats()
        
        print(f"✅ Stats retrieved: {result['success']}")
        if result['success']:
            print(f"   RAG stats: {result['rag_stats']}")
            print(f"   System status: {result['system_info']['status']}")
        
        return result['success']
    except Exception as e:
        print(f"❌ Stats test failed: {e}")
        return False

async def test_content_types_endpoint():
    """Test content types endpoint"""
    print("\n🧪 Testing content types endpoint...")
    
    try:
        api = WebScrapingAPI()
        result = await api.get_content_types()
        
        print(f"✅ Content types: {len(result['content_types'])} types available")
        print(f"   Frequencies: {len(result['scraping_frequencies'])} options")
        
        # Mostra alcuni esempi
        print("   Content types:")
        for ct in result['content_types'][:3]:
            print(f"     - {ct['value']}: {ct['label']}")
        
        return result['success']
    except Exception as e:
        print(f"❌ Content types test failed: {e}")
        return False

async def test_demo_workflow():
    """Test workflow completo demo"""
    print("\n🧪 Testing complete demo workflow...")
    
    try:
        api = WebScrapingAPI()
        
        # 1. Health check
        health = await api.health_check()
        if not health['status'] == 'healthy':
            print("❌ System not healthy")
            return False
        
        # 2. Get content types
        types = await api.get_content_types()
        if not types['success']:
            print("❌ Content types failed")
            return False
        
        # 3. Scrape demo website
        demo_data = {
            "url": "https://example.com",
            "company_name": "Demo Company",
            "respect_robots_txt": True,
            "auto_rag_processing": True
        }
        
        scrape_result = await api.scrape_website(demo_data)
        if not scrape_result['success']:
            print("❌ Demo scraping failed")
            return False
        
        # 4. Get final stats
        final_stats = await api.get_stats()
        if not final_stats['success']:
            print("❌ Final stats failed")
            return False
        
        print("✅ Complete demo workflow successful!")
        print(f"   RAG integrations: {final_stats['rag_stats']['rag_integrations']}")
        print(f"   Documents processed: {final_stats['rag_stats']['documents_processed']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo workflow failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Testing Web Scraping API Functions")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("Scrape Website", test_scrape_endpoint),
        ("Get Stats", test_stats_endpoint),
        ("Content Types", test_content_types_endpoint),
        ("Demo Workflow", test_demo_workflow)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if await test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 60)
    print(f"📊 API Function Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 ALL API FUNCTION TESTS PASSED!")
        print("\n🚀 Web Scraping Module is FULLY OPERATIONAL!")
        return 0
    else:
        print("❌ Some API function tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
