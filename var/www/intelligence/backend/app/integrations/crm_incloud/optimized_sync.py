#!/usr/bin/env python3
"""
OPTIMIZED CRM SYNC - Versione semplificata per test
"""

import os
import time
import logging
from datetime import datetime
from sqlalchemy import create_engine, text
import requests

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("optimized_sync")

# Database
DATABASE_URL = "postgresql://intelligence_user:intelligence_pass@localhost/intelligence"
engine = create_engine(DATABASE_URL)

# CRM Config
try:
    from dotenv import load_dotenv
    load_dotenv('/var/www/intelligence/backend/.env')
except ImportError:
    pass

CRM_API_KEY = os.getenv("CRM_API_KEY")
CRM_USERNAME = os.getenv("CRM_USERNAME")
CRM_PASSWORD = os.getenv("CRM_PASSWORD")
CRM_BASE_URL = os.getenv("CRM_BASE_URL", "https://api.crmincloud.it")

RATE_LIMIT_DELAY = 1.5  # 40 req/min
PAGE_SIZE = 100

class OptimizedSyncManager:
    def __init__(self):
        self.token = None
        self.request_count = 0
        
    def get_crm_token(self):
        """Get CRM token"""
        if self.token:
            return self.token
            
        logger.info("🔐 Getting CRM token...")
        
        url = f"{CRM_BASE_URL}/api/v1/Auth/Login"
        payload = {
            "grant_type": "password",
            "username": CRM_USERNAME,
            "password": CRM_PASSWORD
        }
        headers = {
            "WebApiKey": CRM_API_KEY,
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        self.token = response.json()["access_token"]
        logger.info("✅ Token CRM ottenuto")
        return self.token
    
    def rate_limited_request(self, url, headers):
        """Request con rate limiting"""
        time.sleep(RATE_LIMIT_DELAY)
        self.request_count += 1
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response
    
    def test_sync(self):
        """Test sync con una pagina"""
        logger.info("🧪 Test sync CRM...")
        
        token = self.get_crm_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "WebApiKey": CRM_API_KEY
        }
        
        # Test companies
        companies_url = f"{CRM_BASE_URL}/api/v1/Companies?limit=5"
        response = self.rate_limited_request(companies_url, headers)
        companies = response.json()
        
        logger.info(f"✅ Test OK: {len(companies)} aziende recuperate")
        logger.info(f"📊 Requests fatte: {self.request_count}")
        
        return len(companies)

def main():
    """Main test"""
    sync = OptimizedSyncManager()
    result = sync.test_sync()
    return result > 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
