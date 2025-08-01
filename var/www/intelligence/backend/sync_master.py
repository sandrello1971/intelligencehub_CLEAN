#!/usr/bin/env python3
"""
Sync Master - Orchestratore schedulazione CRM Intelligence
Esegue in sequenza: Aziende → Contatti → Attività Intelligence → Workflow
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
        logging.FileHandler('/var/www/intelligence/logs/sync_master.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("sync_master")

def run_companies_sync():
    """Sync aziende dal CRM"""
    try:
        logger.info("🏢 Avvio sync aziende...")
        
        from app.integrations.crm_incloud.companies_sync import sync_companies_from_crm
        
        # Sync con limite di 20 aziende
        stats = sync_companies_from_crm(limit=20, dry_run=False)
        
        if stats.get('fatal_error'):
            logger.error(f"❌ Errore fatale sync aziende: {stats['fatal_error']}")
            return False
        
        logger.info(f"✅ Sync aziende completato: {stats.get('companies_created', 0)} create, {stats.get('companies_updated', 0)} aggiornate")
        return True
        
    except Exception as e:
        logger.error(f"❌ Errore sync aziende: {e}")
        return False

def run_contacts_sync():
    """Sync contatti dal CRM"""
    try:
        logger.info("👥 Avvio sync contatti...")
        
        from app.integrations.crm_incloud.contacts_sync import sync_contacts_from_crm
        
        # Sync con limite di 30 contatti
        stats = sync_contacts_from_crm(limit=30)
        
        if stats.get('errors', 0) > stats.get('contacts_checked', 1) / 2:
            logger.warning("⚠️ Troppi errori nel sync contatti")
            return False
        
        logger.info(f"✅ Sync contatti completato: {stats.get('contacts_created', 0)} creati, {stats.get('contacts_updated', 0)} aggiornati")
        return True
        
    except Exception as e:
        logger.error(f"❌ Errore sync contatti: {e}")
        return False

def run_activities_sync():
    """Sync attività Intelligence dal CRM"""
    try:
        logger.info("📋 Avvio sync attività Intelligence...")
        
        from crm_activities_sync import run_sync
        
        # Sync con limite di 50 attività
        stats = run_sync(limit=50)
        
        if stats.get('errors', 0) > 5:
            logger.warning("⚠️ Troppi errori nel sync attività")
            return False
        
        logger.info(f"✅ Sync attività completato: {stats.get('activities_inserted', 0)} inserite, {stats.get('activities_skipped', 0)} saltate")
        return True
        
    except Exception as e:
        logger.error(f"❌ Errore sync attività: {e}")
        return False

def run_workflow_generation():
    """Genera workflow per nuove attività"""
    try:
        logger.info("⚡ Avvio generazione workflow...")
        
        # Import per database
        from app.core.database import SessionLocal
        from sqlalchemy import text
        
        # Trova attività senza ticket generato
        db = SessionLocal()
        try:
            query = text("""
                SELECT a.id 
                FROM activities a
                LEFT JOIN tickets t ON t.activity_id = a.id
                WHERE a.crm_activity_id IS NOT NULL 
                AND t.id IS NULL
                ORDER BY a.created_at DESC
                LIMIT 10
            """)
            
            results = db.execute(query).fetchall()
            generated = 0
            
            for row in results:
                try:
                    # Import della funzione workflow
                    from workflow_generator import generate_workflow_for_activity
                    
                    result = generate_workflow_for_activity(row.id)
                    
                    if result.get('success'):
                        generated += 1
                        logger.info(f"✅ Workflow generato per attività {row.id}")
                    else:
                        logger.warning(f"⚠️ Workflow fallito per attività {row.id}: {result.get('errori', 'Errore sconosciuto')}")
                        
                except Exception as e:
                    logger.error(f"❌ Errore workflow attività {row.id}: {e}")
            
            logger.info(f"✅ Generazione workflow completata: {generated} workflow creati")
            return True
            
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"❌ Errore generazione workflow: {e}")
        return False

def main():
    """Processo principale di sync"""
    logger.info("🚀 AVVIO SYNC MASTER - Sequenza completa Intelligence")
    start_time = datetime.now()
    
    success_count = 0
    total_steps = 4
    
    # STEP 1: Sync aziende
    logger.info("=" * 50)
    if run_companies_sync():
        success_count += 1
    
    time.sleep(3)  # Pausa tra sync per evitare rate limiting
    
    # STEP 2: Sync contatti  
    logger.info("=" * 50)
    if run_contacts_sync():
        success_count += 1
    
    time.sleep(3)
    
    # STEP 3: Sync attività Intelligence
    logger.info("=" * 50)
    if run_activities_sync():
        success_count += 1
    
    time.sleep(3)
    
    # STEP 4: Generazione workflow
    logger.info("=" * 50)
    if run_workflow_generation():
        success_count += 1
    
    # Riepilogo finale
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info("=" * 50)
    logger.info(f"🎯 SYNC MASTER COMPLETATO")
    logger.info(f"📊 Successi: {success_count}/{total_steps}")
    logger.info(f"⏱️ Durata: {duration}")
    
    if success_count == total_steps:
        logger.info("🎉 Tutti i sync completati con successo!")
        return 0
    elif success_count >= total_steps - 1:
        logger.info("✅ Sync completato con successo parziale")
        return 0
    else:
        logger.warning(f"⚠️ {total_steps - success_count} sync falliti")
        return 1

if __name__ == "__main__":
    sys.exit(main())
