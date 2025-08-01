#!/usr/bin/env python3
"""
Test Sync Master - Solo verifica connessioni senza modifiche
"""

import sys
import logging

# Aggiungi path
sys.path.append('/var/www/intelligence/backend')
sys.path.append('/var/www/intelligence')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_sync_master")

def test_companies_import():
    """Test import modulo aziende"""
    try:
        from app.integrations.crm_incloud.companies_sync import sync_companies_from_crm
        logger.info("✅ Import companies_sync OK")
        return True
    except Exception as e:
        logger.error(f"❌ Import companies_sync fallito: {e}")
        return False

def test_contacts_import():
    """Test import modulo contatti"""
    try:
        from app.integrations.crm_incloud.contacts_sync import sync_contacts_from_crm
        logger.info("✅ Import contacts_sync OK")
        return True
    except Exception as e:
        logger.error(f"❌ Import contacts_sync fallito: {e}")
        return False

def test_activities_import():
    """Test import modulo attività"""
    try:
        from crm_activities_sync import run_sync
        logger.info("✅ Import activities_sync OK")
        return True
    except Exception as e:
        logger.error(f"❌ Import activities_sync fallito: {e}")
        return False

def test_workflow_import():
    """Test import workflow generator"""
    try:
        from workflow_generator import generate_workflow_for_activity
        logger.info("✅ Import workflow_generator OK")
        return True
    except Exception as e:
        logger.error(f"❌ Import workflow_generator fallito: {e}")
        return False

def test_database_connection():
    """Test connessione database"""
    try:
        from app.core.database import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        result = db.execute(text("SELECT 1")).fetchone()
        db.close()
        
        logger.info("✅ Connessione database OK")
        return True
    except Exception as e:
        logger.error(f"❌ Connessione database fallita: {e}")
        return False

def main():
    """Test tutti i moduli"""
    logger.info("🧪 TEST SYNC MASTER - Verifica imports e connessioni")
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Companies Import", test_companies_import),
        ("Contacts Import", test_contacts_import),
        ("Activities Import", test_activities_import),
        ("Workflow Import", test_workflow_import)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"🔍 Test: {test_name}")
        results[test_name] = test_func()
    
    # Riepilogo
    logger.info("=" * 50)
    logger.info("📊 RIEPILOGO TEST:")
    
    passed = sum(results.values())
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"   {test_name}: {status}")
    
    logger.info(f"🎯 Risultato: {passed}/{total} test superati")
    
    if passed == total:
        logger.info("🎉 Tutti i test OK! Il sync master è pronto.")
        return 0
    else:
        logger.warning("⚠️ Alcuni test falliti. Controllare prima di usare sync master.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
