#!/usr/bin/env python3
"""
Sync Master TEST - Versione con numeri limitati per test
Esegue: 5 Aziende → 5 Contatti → 10 Attività → 3 Workflow
"""

import sys
import time
import logging
from datetime import datetime

# Aggiungi path per importare i moduli
sys.path.append('/var/www/intelligence/backend')
sys.path.append('/var/www/intelligence')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/www/intelligence/logs/sync_master_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("sync_master_test")

def run_companies_sync():
    """Sync aziende dal CRM - TEST con 5 aziende"""
    try:
        logger.info("🏢 TEST: Avvio sync 5 aziende...")
        
        from app.integrations.crm_incloud.companies_sync import sync_companies_from_crm
        
        # TEST: Solo 5 aziende
        stats = sync_companies_from_crm(limit=5, dry_run=False)
        
        if stats.get('fatal_error'):
            logger.error(f"❌ Errore fatale sync aziende: {stats['fatal_error']}")
            return False
        
        logger.info(f"✅ TEST sync aziende OK: {stats.get('companies_created', 0)} create, {stats.get('companies_updated', 0)} aggiornate")
        return True
        
    except Exception as e:
        logger.error(f"❌ Errore sync aziende: {e}")
        return False

def run_contacts_sync():
    """Sync contatti dal CRM - TEST con 5 contatti"""
    try:
        logger.info("👥 TEST: Avvio sync 5 contatti...")
        
        from app.integrations.crm_incloud.contacts_sync import sync_contacts_from_crm
        
        # TEST: Solo 5 contatti
        stats = sync_contacts_from_crm(limit=5)
        
        logger.info(f"✅ TEST sync contatti OK: {stats.get('contacts_created', 0)} creati, {stats.get('contacts_updated', 0)} aggiornati")
        return True
        
    except Exception as e:
        logger.error(f"❌ Errore sync contatti: {e}")
        return False

def run_activities_sync():
    """Sync attività Intelligence - TEST con 10 attività"""
    try:
        logger.info("📋 TEST: Avvio sync 10 attività Intelligence...")
        
        from crm_activities_sync import run_sync
        
        # TEST: Solo 10 attività
        stats = run_sync(limit=10)
        
        logger.info(f"✅ TEST sync attività OK: {stats.get('activities_inserted', 0)} inserite, {stats.get('activities_skipped', 0)} saltate")
        return True
        
    except Exception as e:
        logger.error(f"❌ Errore sync attività: {e}")
        return False

def run_workflow_generation():
    """Genera workflow - TEST con 3 workflow max"""
    try:
        logger.info("⚡ TEST: Avvio generazione 3 workflow...")
        
        from app.core.database import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        try:
            query = text("""
                SELECT a.id, a.crm_activity_id 
                FROM activities a
                LEFT JOIN tickets t ON t.activity_id = a.id
                WHERE a.crm_activity_id IS NOT NULL 
                AND t.id IS NULL
                ORDER BY a.created_at DESC
                LIMIT 3
            """)
            
            results = db.execute(query).fetchall()
            generated = 0
            
            logger.info(f"🔍 Trovate {len(results)} attività senza workflow")
            
            for row in results:
                try:
                    from workflow_generator import generate_workflow_for_activity
                    
                    result = generate_workflow_for_activity(row.id)
                    
                    if result.get('success'):
                        generated += 1
                        logger.info(f"✅ Workflow generato per attività {row.id}")
                    else:
                        logger.warning(f"⚠️ Workflow fallito per attività {row.id}")
                        
                except Exception as e:
                    logger.error(f"❌ Errore workflow attività {row.id}: {e}")
            
            logger.info(f"✅ TEST generazione workflow OK: {generated} workflow creati")
            return True
            
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"❌ Errore generazione workflow: {e}")
        return False

def main():
    """Processo principale di test"""
    logger.info("🧪 AVVIO SYNC MASTER TEST - Numeri limitati")
    start_time = datetime.now()
    
    success_count = 0
    total_steps = 4
    
    # STEP 1: Sync 5 aziende
    logger.info("=" * 50)
    if run_companies_sync():
        success_count += 1
    
    time.sleep(2)
    
    # STEP 2: Sync 5 contatti  
    logger.info("=" * 50)
    if run_contacts_sync():
        success_count += 1
    
    time.sleep(2)
    
    # STEP 3: Sync 10 attività
    logger.info("=" * 50)
    if run_activities_sync():
        success_count += 1
    
    time.sleep(2)
    
    # STEP 4: Generazione 3 workflow
    logger.info("=" * 50)
    if run_workflow_generation():
        success_count += 1
    
    # Riepilogo finale
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info("=" * 50)
    logger.info(f"🎯 SYNC MASTER TEST COMPLETATO")
    logger.info(f"📊 Successi: {success_count}/{total_steps}")
    logger.info(f"⏱️ Durata: {duration}")
    
    if success_count >= 3:  # Accettiamo 3/4 per il test
        logger.info("🎉 Test completato con successo!")
        return 0
    else:
        logger.warning(f"⚠️ Test fallito: troppi errori")
        return 1

if __name__ == "__main__":
    sys.exit(main())
