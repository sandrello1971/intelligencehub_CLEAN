#!/usr/bin/env python3
"""
CRM Companies Sync - Intelligence Platform v5.0
Sincronizza aziende dal CRM InCloud con salvataggio DB
"""

import os
import time
import logging
import requests
from datetime import datetime
from sqlalchemy.orm import Session

# Import dai modelli esistenti
from app.core.database import SessionLocal
from app.models.company import Company

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crm_sync")

# CRM Config dall'env
CRM_API_KEY = os.getenv("CRM_API_KEY")
CRM_USERNAME = os.getenv("CRM_USERNAME") 
CRM_PASSWORD = os.getenv("CRM_PASSWORD")
CRM_BASE_URL = os.getenv("CRM_BASE_URL", "https://api.crmincloud.it")

# Rate limiting
MAX_CALLS_PER_MINUTE = 40
CALL_INTERVAL = 60 / MAX_CALLS_PER_MINUTE

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

def process_company(company_data, db):
    """Process single company and save to DB"""
    company_id = str(company_data["id"])
    
    # Map CRM data to our Company model
    company_info = {
        "id": int(company_id),
        "name": company_data.get("companyName", ""),
        "partita_iva": company_data.get("taxIdentificationNumber", ""),
        "indirizzo": company_data.get("address", ""),
        "settore": company_data.get("description", "")[:100] if company_data.get("description") else ""
    }
    
    # Check if exists
    existing = db.query(Company).filter_by(id=company_id).first()
    
    if not existing:
        # Create new
        new_company = Company(**company_info)
        db.add(new_company)
        logger.info(f"➕ Created: {company_info['name']}")
        return "created"
    else:
        # Update existing
        for key, value in company_info.items():
            setattr(existing, key, value)
        logger.info(f"🔄 Updated: {company_info['name']}")
        return "updated"

def sync_companies_from_crm(limit=20, dry_run=False):
    """Sync companies from CRM with DB save"""
    logger.info(f"🏢 Starting companies sync (limit={limit}, dry_run={dry_run})...")
    
    stats = {
        "companies_checked": 0,
        "companies_created": 0,
        "companies_updated": 0,
        "errors": 0,
        "start_time": datetime.utcnow().isoformat()
    }
    
    db = SessionLocal()
    
    try:
        # Get token
        token = get_crm_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "WebApiKey": CRM_API_KEY
        }
        
        # Get companies list
        companies_url = f"{CRM_BASE_URL}/api/v1/Companies?limit={limit}"
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
                
                if not dry_run:
                    result = process_company(company_data, db)
                    if result == "created":
                        stats["companies_created"] += 1
                    elif result == "updated":
                        stats["companies_updated"] += 1
                else:
                    logger.info(f"🔍 DRY RUN: {company_data.get('companyName', 'N/A')}")
                
            except Exception as e:
                logger.error(f"❌ Error processing company {company_id}: {e}")
                stats["errors"] += 1
        
        # Commit to database
        if not dry_run:
            db.commit()
            logger.info("✅ Database commit successful")
        
        stats["end_time"] = datetime.utcnow().isoformat()
        return stats
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Fatal error: {e}")
        stats["fatal_error"] = str(e)
        return stats
    finally:
        db.close()

if __name__ == "__main__":
    # Test con 5 companies in dry-run
    result = sync_companies_from_crm(limit=5, dry_run=True)
    print("📊 SYNC RESULTS:")
    for key, value in result.items():
        print(f"  {key}: {value}")
