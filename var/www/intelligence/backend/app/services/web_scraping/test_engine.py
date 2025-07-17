#!/usr/bin/env python3
"""
Test Web Scraping Engine
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.scraped_data import ScrapedWebsiteModel
from scraping_engine import IntelligenceWebScrapingEngine

async def test_basic_scraping():
    """Test basic scraping functionality"""
    print("🧪 Testing Web Scraping Engine...")
    
    # Test website
    website = ScrapedWebsiteModel(
        id=1,
        url="https://example.com",
        company_name="Example Company",
        respect_robots_txt=True
    )
    
    try:
        async with IntelligenceWebScrapingEngine(rate_limit_delay=1.0) as engine:
            results = await engine.scrape_website(website)
            
            print(f"✅ Scraping completed!")
            print(f"   Status: {results['status']}")
            print(f"   Pages scraped: {results['pages_scraped']}")
            print(f"   Content extracted: {len(results['content_extracted'])}")
            print(f"   Contacts found: {len(results['contacts_found'])}")
            print(f"   Companies found: {len(results['companies_found'])}")
            
            # Show stats
            stats = engine.get_stats()
            print(f"   Engine stats: {stats}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🚀 Testing Intelligence Web Scraping Engine")
    print("=" * 60)
    
    success = await test_basic_scraping()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Engine test completed successfully!")
    else:
        print("❌ Engine test failed!")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
