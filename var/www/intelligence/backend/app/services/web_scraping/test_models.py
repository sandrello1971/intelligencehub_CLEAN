#!/usr/bin/env python3
"""
Test modelli web scraping
"""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.scraped_data import (
    ScrapedWebsiteModel, 
    ScrapedContentModel, 
    ScrapedContactModel,
    ScrapedCompanyModel,
    ContentType,
    ScrapingFrequency
)

def test_scraped_website_model():
    """Test ScrapedWebsiteModel"""
    print("🧪 Testing ScrapedWebsiteModel...")
    
    # Dati test
    website_data = {
        "url": "https://example.com",
        "domain": "example.com",
        "title": "Example Company",
        "scraping_frequency": "weekly",
        "company_name": "Example S.r.l.",
        "partita_iva": "12345678901",
        "sector": "Technology"
    }
    
    try:
        website = ScrapedWebsiteModel(**website_data)
        print(f"✅ Website model created: {website.company_name}")
        print(f"   URL: {website.url}")
        print(f"   Frequency: {website.scraping_frequency}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_scraped_content_model():
    """Test ScrapedContentModel"""
    print("\n🧪 Testing ScrapedContentModel...")
    
    content_data = {
        "website_id": 1,
        "page_url": "https://example.com/about",
        "page_title": "About Us",
        "content_type": "company_info",
        "confidence_score": 0.85,
        "structured_data": {
            "company_name": "Example S.r.l.",
            "description": "Leading technology company"
        }
    }
    
    try:
        content = ScrapedContentModel(**content_data)
        print(f"✅ Content model created: {content.page_title}")
        print(f"   Type: {content.content_type}")
        print(f"   Confidence: {content.confidence_score}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_scraped_contact_model():
    """Test ScrapedContactModel"""
    print("\n🧪 Testing ScrapedContactModel...")
    
    contact_data = {
        "scraped_content_id": 1,
        "full_name": "Mario Rossi",
        "first_name": "Mario",
        "last_name": "Rossi",
        "email": "mario.rossi@example.com",
        "phone": "+39 123 456 7890",
        "position": "CEO",
        "company_name": "Example S.r.l.",
        "confidence_score": 0.92
    }
    
    try:
        contact = ScrapedContactModel(**contact_data)
        print(f"✅ Contact model created: {contact.full_name}")
        print(f"   Email: {contact.email}")
        print(f"   Position: {contact.position}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_scraped_company_model():
    """Test ScrapedCompanyModel"""
    print("\n🧪 Testing ScrapedCompanyModel...")
    
    company_data = {
        "scraped_content_id": 1,
        "company_name": "Example S.r.l.",
        "description": "Leading technology company in Italy",
        "sector": "Technology",
        "company_size": "medium",
        "website": "https://example.com",
        "email": "info@example.com",
        "phone": "+39 123 456 7890",
        "address_city": "Milano",
        "partita_iva": "12345678901",
        "services_offered": ["Software Development", "AI Consulting"],
        "confidence_score": 0.88,
        "data_completeness": 0.75
    }
    
    try:
        company = ScrapedCompanyModel(**company_data)
        print(f"✅ Company model created: {company.company_name}")
        print(f"   Sector: {company.sector}")
        print(f"   P.IVA: {company.partita_iva}")
        print(f"   Services: {len(company.services_offered or [])}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_json_serialization():
    """Test serializzazione JSON"""
    print("\n🧪 Testing JSON serialization...")
    
    try:
        website = ScrapedWebsiteModel(
            url="https://test.com",
            company_name="Test Company",
            created_at=datetime.now()
        )
        
        json_data = website.model_dump_json()
        print(f"✅ JSON serialization successful")
        print(f"   Length: {len(json_data)} characters")
        
        # Test deserialization
        parsed_data = json.loads(json_data)
        website_restored = ScrapedWebsiteModel(**parsed_data)
        print(f"✅ JSON deserialization successful")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Web Scraping Models")
    print("=" * 50)
    
    tests = [
        test_scraped_website_model,
        test_scraped_content_model,
        test_scraped_contact_model,
        test_scraped_company_model,
        test_json_serialization
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
