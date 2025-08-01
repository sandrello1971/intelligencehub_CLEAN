#!/usr/bin/env python3
"""
CRM Contacts Sync - Intelligence Platform v5.0
Sincronizza contatti dal CRM InCloud con salvataggio DB
"""

import os
import time
import logging
import requests
import json
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# CARICAMENTO .ENV
try:
    from dotenv import load_dotenv
    load_dotenv('/var/www/intelligence/backend/.env')
except ImportError:
    env_file = '/var/www/intelligence/backend/.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("contacts_sync")

# Database
DATABASE_URL = "postgresql://intelligence_user:intelligence_pass@localhost/intelligence"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# CRM Config
CRM_API_KEY = os.getenv("CRM_API_KEY")
CRM_USERNAME = os.getenv("CRM_USERNAME") 
CRM_PASSWORD = os.getenv("CRM_PASSWORD")
CRM_BASE_URL = os.getenv("CRM_BASE_URL", "https://api.crmincloud.it")

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

def process_contact(contact_data, db):
    """Process a single contact with company verification"""
    contact_id = contact_data.get("id")
    company_id = contact_data.get("companyId")
    
    # Se non ha company_id, saltiamo il contatto
    if not company_id:
        logger.info(f"⏭️ Contatto {contact_id} senza azienda - saltato")
        return "skipped"
    
    # Verifica se company_id esiste nella tabella companies
    company_check = text("SELECT id FROM companies WHERE id = :company_id")
    company_exists = db.execute(company_check, {"company_id": str(company_id)}).fetchone()
    
    if not company_exists:
        logger.warning(f"⚠️ Company {company_id} non trovata per contatto {contact_id} - saltato")
        return "skipped"
    
    # Verifica se il contatto esiste già
    existing_query = text("SELECT id FROM contacts WHERE note LIKE :crm_id_pattern")
    crm_id_pattern = f"%ID: {contact_id}%"
    existing = db.execute(existing_query, {"crm_id_pattern": crm_id_pattern}).fetchone()
    
    # Prepara info contatto
    contact_info = {
        "company_id": str(company_id),
        "nome": contact_data.get("name", ""),
        "cognome": contact_data.get("surname", ""),
        "codice": str(contact_data.get("code", "")),
        "indirizzo": contact_data.get("address", ""),
        "citta": contact_data.get("city", ""),
        "cap": contact_data.get("zipCode", ""),
        "provincia": contact_data.get("province", ""),
        "regione": contact_data.get("region", ""),
        "stato": contact_data.get("country", ""),
        "ruolo_aziendale": contact_data.get("jobTitle", ""),
        "email": contact_data.get("email"),
        "telefono": contact_data.get("phone", ""),
        "note": f"Importato da CRM - ID: {contact_id}",
        "sorgente": "CRM_INCLOUD",
        "data_nascita": None,
        "luogo_nascita": contact_data.get("birthPlace", ""),
        "codice_fiscale": contact_data.get("taxCode", "")
    }
    
    if not existing:
        # Create new contact
        insert_query = text("""
        INSERT INTO contacts (
            company_id, nome, cognome, codice, indirizzo, citta, cap, 
            provincia, regione, stato, ruolo_aziendale, email, telefono,
            note, sorgente, data_nascita, luogo_nascita, codice_fiscale
        ) VALUES (
            :company_id, :nome, :cognome, :codice, :indirizzo, :citta, :cap,
            :provincia, :regione, :stato, :ruolo_aziendale, :email, :telefono,
            :note, :sorgente, :data_nascita, :luogo_nascita, :codice_fiscale
        )
        """)
        
        db.execute(insert_query, contact_info)
        logger.info(f"➕ Created contact: {contact_info['nome']} {contact_info['cognome']}")
        return "created"
    else:
        # Update existing contact
        update_query = text("""
        UPDATE contacts SET 
            company_id = :company_id, nome = :nome, cognome = :cognome,
            codice = :codice, indirizzo = :indirizzo, citta = :citta, cap = :cap,
            provincia = :provincia, regione = :regione, stato = :stato,
            ruolo_aziendale = :ruolo_aziendale, email = :email, telefono = :telefono,
            data_nascita = :data_nascita, luogo_nascita = :luogo_nascita,
            codice_fiscale = :codice_fiscale
        WHERE id = :contact_id
        """)
        
        contact_info["contact_id"] = existing[0]
        db.execute(update_query, contact_info)
        logger.info(f"🔄 Updated contact: {contact_info['nome']} {contact_info['cognome']}")
        return "updated"

def sync_contacts_from_crm(limit=50):
    """Sync contacts from CRM"""
    logger.info(f"👥 Starting contacts sync (limit={limit})...")
    
    stats = {
        "contacts_checked": 0,
        "contacts_created": 0, 
        "contacts_updated": 0,
        "contacts_skipped": 0,
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
        
        # Get contacts list
        contacts_url = f"{CRM_BASE_URL}/api/v1/Contacts?limit={limit}"
        logger.info(f"📡 Fetching contacts from CRM...")
        response = rate_limited_request(contacts_url, headers)
        contact_ids = response.json()
        
        logger.info(f"📊 Processing {len(contact_ids)} contacts...")
        
        # Process each contact
        for i, contact_id in enumerate(contact_ids[:limit]):
            try:
                stats["contacts_checked"] += 1
                
                # Get contact details
                contact_detail_url = f"{CRM_BASE_URL}/api/v1/Contacts/{contact_id}"
                contact_response = rate_limited_request(contact_detail_url, headers)
                contact_data = contact_response.json()
                
                # Process contact
                result = process_contact(contact_data, db)
                
                if result == "created":
                    stats["contacts_created"] += 1
                elif result == "updated":
                    stats["contacts_updated"] += 1
                elif result == "skipped":
                    stats["contacts_skipped"] += 1
                
                # Commit ogni 10 contatti
                if (i + 1) % 10 == 0:
                    db.commit()
                    logger.info(f"💾 Committed batch {i + 1}/{len(contact_ids)}")
                
            except Exception as e:
                logger.error(f"❌ Error processing contact {contact_id}: {e}")
                stats["errors"] += 1
                continue
        
        # Final commit
        db.commit()
        
        # Final stats
        stats["end_time"] = datetime.utcnow().isoformat()
        logger.info(f"✅ Contacts sync completed: {json.dumps(stats, indent=2)}")
        
        return stats
        
    except Exception as e:
        db.rollback()
        logger.error(f"💥 Contacts sync failed: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    sync_contacts_from_crm(limit=20)
