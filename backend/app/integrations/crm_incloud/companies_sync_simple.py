#!/usr/bin/env python3
"""
CRM Companies Sync SIMPLE - Con caricamento .env esplicito
"""

import os
import time
import logging
import requests
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# CARICAMENTO ESPLICITO .ENV
try:
    from dotenv import load_dotenv
    load_dotenv('/var/www/intelligence/backend/.env')
except ImportError:
    # Fallback manuale se dotenv non disponibile
    env_file = '/var/www/intelligence/backend/.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crm_sync_simple")

# Database URL
DATABASE_URL = "postgresql://intelligence_user:intelligence_pass@localhost/intelligence"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# CRM Config
CRM_API_KEY = os.getenv("CRM_API_KEY")
CRM_USERNAME = os.getenv("CRM_USERNAME") 
CRM_PASSWORD = os.getenv("CRM_PASSWORD")
CRM_BASE_URL = os.getenv("CRM_BASE_URL", "https://api.crmincloud.it")

# Debug variabili
logger.info(f"CRM_USERNAME: {CRM_USERNAME}")
logger.info(f"CRM_BASE_URL: {CRM_BASE_URL}")
logger.info(f"CRM_API_KEY: {'***' if CRM_API_KEY else 'None'}")

# Rate limiting
CALL_INTERVAL = 60 / 40  # 40 req/min

def get_crm_token():
    """Get CRM authentication token"""
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
    
    logger.info("🔐 Getting CRM token...")
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["access_token"]

def rate_limited_request(url, headers):
    """Request with rate limiting"""
    time.sleep(CALL_INTERVAL)
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response

def sync_companies_simple(limit=20):
    """Sync companies usando SQL diretto"""
    logger.info(f"🏢 Starting simple companies sync (limit={limit})...")
    
    stats = {"companies_checked": 0, "companies_created": 0, "companies_updated": 0, "errors": 0}
    
    db = SessionLocal()
    
    try:
        # Get token
        token = get_crm_token()
        headers = {"Authorization": f"Bearer {token}", "WebApiKey": CRM_API_KEY}
        
        # Get companies list
        companies_url = f"{CRM_BASE_URL}/api/v1/Companies?limit={limit}"
        logger.info(f"📡 Fetching companies from CRM...")
        response = rate_limited_request(companies_url, headers)
        company_ids = response.json()
        
        logger.info(f"📊 Processing {len(company_ids)} companies...")
        
        # Process each company
        for company_id in company_ids:
            try:
                # Get company details
                detail_url = f"{CRM_BASE_URL}/api/v1/Company/{company_id}"
                detail_response = rate_limited_request(detail_url, headers)
                company_data = detail_response.json()
                
                stats["companies_checked"] += 1
                
                # Check if exists
                check_sql = text("SELECT COUNT(*) FROM companies WHERE id = :company_id")
                result = db.execute(check_sql, {"company_id": str(company_id)})
                exists = result.scalar() > 0
                
                # Prepare data
                company_name = company_data.get("companyName", "")
                partita_iva = company_data.get("taxIdentificationNumber", "")
                address = company_data.get("address", "")
                sector = company_data.get("description", "")[:100] if company_data.get("description") else ""
                
                if not exists:
                    # Insert new
                    insert_sql = text("""
                        INSERT INTO companies (id, name, partita_iva, indirizzo, settore, created_at) 
                        VALUES (:id, :name, :partita_iva, :indirizzo, :settore, NOW())
                    """)
                    db.execute(insert_sql, {
                        "id": str(company_id),
                        "name": company_name,
                        "partita_iva": partita_iva,
                        "indirizzo": address,
                        "settore": sector
                    })
                    stats["companies_created"] += 1
                    logger.info(f"➕ Created: {company_name} (ID: {company_id})")
                else:
                    # Update existing
                    update_sql = text("""
                        UPDATE companies 
                        SET name = :name, partita_iva = :partita_iva, indirizzo = :indirizzo, settore = :settore
                        WHERE id = :id
                    """)
                    db.execute(update_sql, {
                        "id": str(company_id),
                        "name": company_name,
                        "partita_iva": partita_iva,
                        "indirizzo": address,
                        "settore": sector
                    })
                    stats["companies_updated"] += 1
                    logger.info(f"🔄 Updated: {company_name} (ID: {company_id})")
                
            except Exception as e:
                logger.error(f"❌ Error processing company {company_id}: {e}")
                stats["errors"] += 1
        
        # Commit
        db.commit()
        logger.info("✅ Database commit successful")
        
        return stats
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Fatal error: {e}")
        return {"fatal_error": str(e)}
    finally:
        db.close()

if __name__ == "__main__":
    result = sync_companies_simple(limit=10)
    print("📊 SIMPLE SYNC RESULTS:", result)
