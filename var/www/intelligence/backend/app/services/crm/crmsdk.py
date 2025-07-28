from typing import Optional
from sqlalchemy.orm import Session
import os
import requests
from sqlalchemy import text

CRM_API_KEY = os.getenv("CRM_API_KEY")
CRM_BASE_URL = "https://api.crmincloud.it/api/v1"

def get_crm_token():
    """Get CRM authentication token - da implementare con credenziali reali"""
    # TODO: Implementa autenticazione CRM reale
    return "dummy_token"

def create_crm_activity(data: dict) -> int:
    """
    Crea un'attività nel CRM e restituisce l'ID creato.
    """
    # TODO: Implementa creazione attività CRM reale
    print(f"[CRM] Creating activity: {data.get('subject', 'No subject')}")
    print(f"[CRM] Company ID: {data.get('companyId')}")
    print(f"[CRM] Description: {data.get('description', '')[:100]}...")
    return 12345  # Mock ID per ora

def get_company_id_by_name(company_name: str, db: Session) -> Optional[int]:
    """Trova company_id con fuzzy matching"""
    if not company_name or not company_name.strip():
        print(f"[CRM] ❌ Empty company name")
        return None
    
    company_name = company_name.strip()
    print(f"[CRM] 🔍 Searching for: '{company_name}'")
    
    try:
        # Exact match
        exact = db.execute(
            text("SELECT id, nome FROM companies WHERE LOWER(nome) LIKE LOWER(:pattern)"),
            {"pattern": f"%{company_name}%"}
        ).fetchone()
        
        if exact:
            print(f"[CRM] ✅ EXACT MATCH: '{company_name}' → '{exact[1]}' (ID: {exact[0]})")
            return exact[0]
        
        print(f"[CRM] ❌ NO MATCH found for: '{company_name}'")
        return None
        
    except Exception as e:
        print(f"[CRM] 💥 DATABASE ERROR: {e}")
        return None

