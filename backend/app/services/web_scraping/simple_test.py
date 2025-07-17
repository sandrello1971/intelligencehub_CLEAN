#!/usr/bin/env python3
"""
Test semplificato modelli
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from models.scraped_data import ScrapedWebsiteModel, ContentType
    
    print("🧪 Testing ScrapedWebsiteModel...")
    
    website = ScrapedWebsiteModel(
        url="https://example.com",
        company_name="Test Company"
    )
    
    print(f"✅ Model created: {website.company_name}")
    print(f"✅ URL: {website.url}")
    print(f"✅ Frequency: {website.scraping_frequency}")
    
    print("\n🎉 Basic model test passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
