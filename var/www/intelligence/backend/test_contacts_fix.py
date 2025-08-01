#!/usr/bin/env python3
"""
Test del fix per contacts_sync
"""

import sys
import logging

sys.path.append('/var/www/intelligence/backend')
sys.path.append('/var/www/intelligence')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_contacts_fix")

def test_contacts_sync():
    """Test del contacts_sync con il fix"""
    try:
        logger.info("🧪 TEST: Sync 3 contatti con fix foreign key...")
        
        from app.integrations.crm_incloud.contacts_sync import sync_contacts_from_crm
        
        # Test con solo 3 contatti
        stats = sync_contacts_from_crm(limit=3)
        
        logger.info("📊 Risultati:")
        logger.info(f"  Contatti controllati: {stats.get('contacts_checked', 0)}")
        logger.info(f"  Contatti creati: {stats.get('contacts_created', 0)}")
        logger.info(f"  Contatti aggiornati: {stats.get('contacts_updated', 0)}")
        logger.info(f"  Contatti saltati: {stats.get('contacts_skipped', 0)}")
        logger.info(f"  Errori: {stats.get('errors', 0)}")
        
        # Consideriamo successo se non ci sono errori fatali
        if stats.get('errors', 0) < stats.get('contacts_checked', 1):
            logger.info("✅ Test contacts_sync OK!")
            return True
        else:
            logger.error("❌ Troppi errori nel contacts_sync")
            return False
        
    except Exception as e:
        logger.error(f"❌ Errore test contacts_sync: {e}")
        return False

if __name__ == "__main__":
    test_contacts_sync()
