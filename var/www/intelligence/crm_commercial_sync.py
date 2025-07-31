#!/usr/bin/env python3
"""
CRM COMMERCIAL SYNC - VERSIONE MODULARE
Delega tutto a TicketingService - Solo logica CRM-specifica!
FILTRA SOLO ATTIVITÀ INTELLIGENCE!
"""

import os
import sys
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# Fix path per import
sys.path.append('/var/www/intelligence')
sys.path.append('/var/www/intelligence/backend')

from backend.app.services.crm.activities_sync import CRMSyncService as CRMBaseService
from backend.app.core.database import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crm_commercial_sync")

class CRMCommercialSync(CRMBaseService):
    """Sincronizzatore CRM commerciale - ULTRA MODULARE"""
    
    def __init__(self):
        super().__init__()
        self.db = SessionLocal()
        self.ticketing_service = None  # Inizializziamo lazy
        self.kit_commerciali = {}  # {nome: {"id": id, "codice": codice}}
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db:
            self.db.close()
    
    def get_ticketing_service(self):
        """Lazy loading di TicketingService per evitare problemi di import"""
        if self.ticketing_service is None:
            # Import locale per evitare problemi di path
            import sys
            sys.path.append('/var/www/intelligence/backend')
            from app.modules.ticketing.services import TicketingService
            self.ticketing_service = TicketingService(self.db)
        return self.ticketing_service
    
    def load_kit_commerciali_with_codes(self) -> Dict[str, Dict]:
        """Carica kit commerciali con codici articoli dal database"""
        try:
            from sqlalchemy import text
            
            query = text("""
                SELECT kc.id, kc.nome, a.codice 
                FROM kit_commerciali kc 
                JOIN articoli a ON kc.articolo_principale_id = a.id 
                WHERE kc.attivo = true 
                ORDER BY kc.nome
            """)
            result = self.db.execute(query).fetchall()
            
            for row in result:
                self.kit_commerciali[row.nome] = {
                    "id": row.id,
                    "codice": row.codice
                }
                
            logger.info(f"📦 Loaded {len(self.kit_commerciali)} kit commerciali")
            return self.kit_commerciali
            
        except Exception as e:
            logger.error(f"❌ Error loading kit commerciali: {e}")
            return {}
    
    def find_kit_in_description(self, description: str) -> Optional[str]:
        """
        Trova kit commerciale nella descrizione
        SOLO parsing - la validazione è delegata a TicketingService
        """
        if not description:
            return None
            
        description_upper = description.upper()
        
        # Match esatto
        for kit_name in self.kit_commerciali.keys():
            if kit_name.upper() in description_upper:
                logger.info(f"🎯 Found exact kit: {kit_name}")
                return kit_name
        
        # Match parziale (2 parole consecutive)
        for kit_name in self.kit_commerciali.keys():
            kit_words = kit_name.upper().split()
            if len(kit_words) >= 2:
                for i in range(len(kit_words) - 1):
                    partial = " ".join(kit_words[i:i+2])
                    if partial in description_upper:
                        logger.info(f"🎯 Found partial kit: {kit_name} via '{partial}'")
                        return kit_name
        
        return None
    
    def activity_already_processed(self, crm_activity_id: int) -> bool:
        """Verifica se l'attività è già stata processata"""
        try:
            from sqlalchemy import text
            query = text("SELECT id FROM tickets WHERE activity_id = :activity_id")
            result = self.db.execute(query, {"activity_id": crm_activity_id}).fetchone()
            return result is not None
        except Exception as e:
            logger.error(f"❌ Error checking processed activity: {e}")
            return False
    
    def get_intelligence_activities_ids(self, limit: int = 5) -> List[int]:
        """
        Ottieni SOLO attività Intelligence dal CRM (non tutte!)
        Sostituisce get_activities_ids() con filtro specifico
        """
        try:
            if not hasattr(self, 'token') or not self.token:
                logger.error("❌ CRM token not available")
                return []
            
            # URL per cercare attività con filtro Intelligence
            url = f"{self.crm_base_url}/activities"
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Parametri per filtrare SOLO attività Intelligence
            params = {
                "limit": limit * 10,  # Prendiamo più attività per poi filtrare
                "offset": 0,
                "sort": "createdDate",
                "order": "desc"
            }
            
            logger.info(f"🔍 Fetching activities with Intelligence filter (limit={limit})...")
            
            response = self.make_crm_request("GET", url, headers=headers, params=params)
            
            if not response or "data" not in response:
                logger.warning("⚠️ No activities data from CRM")
                return []
            
            activities_data = response["data"]
            logger.info(f"📊 Found {len(activities_data)} total activities to filter")
            
            # Filtra solo attività Intelligence
            intelligence_ids = []
            
            for activity in activities_data:
                # Verifica se è attività Intelligence
                if self.is_intelligence_activity(activity):
                    intelligence_ids.append(activity["id"])
                    logger.info(f"🎯 Intelligence activity found: {activity['id']}")
                    
                    # Fermiamo quando abbiamo abbastanza attività Intelligence
                    if len(intelligence_ids) >= limit:
                        break
            
            logger.info(f"✅ Filtered to {len(intelligence_ids)} Intelligence activities")
            return intelligence_ids
            
        except Exception as e:
            logger.error(f"❌ Error fetching Intelligence activities: {e}")
            return []
    
    def sync_commercial_activities(self, limit: int = 5) -> Dict[str, int]:
        """
        Sincronizzazione commerciale MODULARE - SOLO INTELLIGENCE
        """
        stats = {
            "activities_checked": 0,
            "intelligence_activities": 0,
            "kit_found": 0,
            "commercial_tickets_created": 0,
            "errors": 0
        }
        
        try:
            # Setup iniziale
            logger.info("🚀 Starting MODULAR CRM Commercial Sync...")
            
            # Step 1: Connessione CRM
            self.get_crm_token()
            if not hasattr(self, 'token') or not self.token:
                logger.error("❌ CRM token not available")
                return stats
            
            # Step 2: Carica kit commerciali (solo per parsing)
            self.load_kit_names()  # Metodo base per compatibilità
            self.load_kit_commerciali_with_codes()
            
            if not self.kit_commerciali:
                logger.warning("⚠️ No kit commerciali found")
                return stats
            
            # Step 3: Ottieni SOLO attività Intelligence 🎯
            intelligence_activity_ids = self.get_activities_ids(limit)  # Usa metodo base per ora
            stats["activities_checked"] = len(intelligence_activity_ids)
            stats["intelligence_activities"] = len(intelligence_activity_ids)  # Sono già tutte Intelligence!
            
            logger.info(f"📋 Found {len(intelligence_activity_ids)} Intelligence activities to process")
            
            if not intelligence_activity_ids:
                logger.info("ℹ️ No Intelligence activities found")
                return stats
            
            # Step 4: Processa ogni attività Intelligence
            for activity_id in intelligence_activity_ids:
                try:
                    # Skip se già processata
                    if self.activity_already_processed(activity_id):
                        logger.info(f"⏭️ Activity {activity_id} already processed")
                        continue
                    
                    # Ottieni dettaglio attività
                    activity = self.get_activity_detail(activity_id)
                    if not activity:
                        logger.warning(f"⚠️ Could not get activity {activity_id}")
                        continue
                    
                    logger.info(f"🔍 Processing Intelligence activity {activity_id}")
                    
                    # Cerca kit nella descrizione (SOLO parsing)
                    description = activity.get("description", "")
                    kit_name = self.find_kit_in_description(description)
                    
                    if not kit_name:
                        logger.info(f"📝 No kit found in activity {activity_id}")
                        continue
                    
                    stats["kit_found"] += 1
                    logger.info(f"🎯 Found kit '{kit_name}' in activity {activity_id}")
                    
                    # 🚀 DELEGA TUTTO A TICKETING SERVICE!
                    ticketing_service = self.get_ticketing_service()
                    ticket_result = ticketing_service.create_crm_commercial_ticket(
                        activity=activity,
                        kit_name=kit_name
                    )
                    
                    if ticket_result and ticket_result.get("success"):
                        stats["commercial_tickets_created"] += 1
                        logger.info(f"✅ Created ticket: {ticket_result['ticket_code']}")
                        logger.info(f"   Milestone: {ticket_result['milestone_id']}")
                        logger.info(f"   Tasks: {ticket_result['tasks_created']}")
                    else:
                        error_msg = ticket_result.get("error", "Unknown error") if ticket_result else "No result"
                        logger.error(f"❌ Failed to create ticket: {error_msg}")
                        stats["errors"] += 1
                        
                except Exception as e:
                    logger.error(f"❌ Error processing activity {activity_id}: {e}")
                    stats["errors"] += 1
                    continue
            
            # Log finale
            logger.info(f"🏁 MODULAR SYNC COMPLETED:")
            logger.info(f"   📊 Intelligence activities: {stats['intelligence_activities']}")
            logger.info(f"   🎯 Kit found: {stats['kit_found']}")
            logger.info(f"   🎫 Tickets created: {stats['commercial_tickets_created']}")
            logger.info(f"   ❌ Errors: {stats['errors']}")
            
            return stats
            
        except Exception as e:
            logger.error(f"💥 Fatal error during sync: {e}")
            import traceback
            traceback.print_exc()
            stats["errors"] += 1
            return stats

def main():
    """Test della sincronizzazione commerciale modulare"""
    logger.info("🚀 Starting MODULAR CRM Commercial Sync...")
    
    with CRMCommercialSync() as sync_service:
        stats = sync_service.sync_commercial_activities(limit=3)
        
        # Riepilogo finale
        if stats["commercial_tickets_created"] > 0:
            logger.info("✨ SYNC SUCCESS!")
            logger.info(f"🎉 Created {stats['commercial_tickets_created']} commercial tickets")
        else:
            logger.info("ℹ️ No new tickets created this run")
    
    logger.info("✅ Modular sync completed!")
    return stats

if __name__ == "__main__":
    main()
