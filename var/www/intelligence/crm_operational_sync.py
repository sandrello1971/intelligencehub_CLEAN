
#!/usr/bin/env python3
"""
CRM OPERATIONAL SYNC - VERSIONE PULITA E CORRETTA
Crea tickets operativi con workflow, milestone e task
"""

import os
import sys
import time
import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

# Add path per import
sys.path.append('/var/www/intelligence')
from backend.app.services.crm.activities_sync import CRMSyncService as CRMBaseService
from backend.app.core.database import SessionLocal

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crm_operational_sync")

# Costanti workflow
WORKFLOW_MILESTONE_ID = 3  # "invio incarico in firma"
WORKFLOW_MILESTONE_NAME = "invio incarico in firma"

# Template task standard (verificati dalla tabella tasks esistenti)
STANDARD_TASKS = [
    {
        "title": "Predisposizione Incarico",
        "description": "viene predisposto l'incarico per l'invio",
        "ordine": 1,
        "sla_giorni": 2
    },
    {
        "title": "Invio Incarico", 
        "description": "con yousign inviare incarico al cliente",
        "ordine": 2,
        "sla_giorni": 1
    },
    {
        "title": "Firma Incarico",
        "description": "riceviamo la firma dell'incarico da parte del cliente", 
        "ordine": 3,
        "sla_giorni": 7
    },
    {
        "title": "Invio Mail di Benvenuto",
        "description": "invio mail di benvenuto secondo il modello standard",
        "ordine": 4, 
        "sla_giorni": 1
    }
]

class CRMOperationalSync(CRMBaseService):
    """Sincronizzatore CRM con workflow operativo completo"""
    
    def __init__(self):
        super().__init__()
        self.db = SessionLocal()
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db:
            self.db.close()
    
    def create_milestone(self, ticket_id: str, kit_name: str) -> Optional[str]:
        """Crea milestone operativa per il ticket"""
        try:
            milestone_id = str(uuid.uuid4())
            
            # Query CORRETTA per milestones (senza created_at)
            insert_query = text("""
                INSERT INTO milestones (
                    id, title, descrizione, workflow_milestone_id
                ) VALUES (
                    :id, :title, :descrizione, :workflow_milestone_id
                ) RETURNING id
            """)
            
            result = self.db.execute(insert_query, {
                "id": milestone_id,
                "title": WORKFLOW_MILESTONE_NAME,
                "descrizione": f"Milestone per {kit_name}",
                "workflow_milestone_id": WORKFLOW_MILESTONE_ID
            }).fetchone()
            
            if result:
                logger.info(f"✅ Created milestone {milestone_id} for ticket {ticket_id}")
                return milestone_id
            return None
            
        except Exception as e:
            logger.error(f"❌ Error creating milestone: {e}")
            return None
    
    def create_tasks(self, milestone_id: str, ticket_id: str) -> int:
        """Crea task standard per la milestone"""
        created_count = 0
        
        try:
            for task_template in STANDARD_TASKS:
                task_id = str(uuid.uuid4())
                
                # Query CORRETTA per tasks (con created_at automatico)
                insert_query = text("""
                    INSERT INTO tasks (
                        id, title, description, status, priorita,
                        milestone_id, ticket_id, sla_giorni, ordine
                    ) VALUES (
                        :id, :title, :description, :status, :priorita,
                        :milestone_id, :ticket_id, :sla_giorni, :ordine
                    )
                """)
                
                self.db.execute(insert_query, {
                    "id": task_id,
                    "title": task_template["title"],
                    "description": task_template["description"],
                    "status": "todo",
                    "priorita": "normale",
                    "milestone_id": milestone_id,
                    "ticket_id": ticket_id,
                    "sla_giorni": task_template["sla_giorni"],
                    "ordine": task_template["ordine"]
                })
                
                created_count += 1
                logger.info(f"✅ Created task: {task_template['title']}")
            
            return created_count
            
        except Exception as e:
            logger.error(f"❌ Error creating tasks: {e}")
            return 0
    
    def create_operational_ticket(self, activity: Dict, kit_name: str) -> Optional[str]:
        """
        Crea ticket operativo completo con workflow
        
        Args:
            activity: Dati dell'attività CRM
            kit_name: Nome del kit commerciale
            
        Returns:
            ID del ticket creato o None se errore
        """
        try:
            # 1. Inserisci attività CRM nella tabella activities locale
            local_activity_id = self.insert_crm_activity_to_local(activity)
            if not local_activity_id:
                logger.error(f"❌ Failed to insert CRM activity {activity['id']}")
                return None
            
            # 2. Crea ticket principale
            ticket_id = str(uuid.uuid4())
            subject = f"{kit_name}"
            
            description = f"Ticket generato automaticamente da attività CRM Intelligence.\n\n"
            description += f"🎯 Kit Commerciale: {kit_name}\n"
            description += f"Attività CRM ID: {activity['id']}\n"
            if activity.get("description"):
                description += f"\nDescrizione originale:\n{activity['description']}"
            
            # Trova company_id
            company_id = None
            if activity.get("companyId"):
                company_id = self.find_company_by_crm_id(activity["companyId"])
            
            # Query CORRETTA per tickets
            insert_ticket_query = text("""
                INSERT INTO tickets (
                    id, title, description, priority, status, 
                    company_id, activity_id, created_at
                ) VALUES (
                    :id, :title, :description, :priority, :status,
                    :company_id, :activity_id, :created_at
                ) RETURNING id
            """)
            
            result = self.db.execute(insert_ticket_query, {
                "id": ticket_id,
                "title": subject,
                "description": description,
                "priority": "media",
                "status": "aperto",
                "company_id": company_id,
                "activity_id": local_activity_id,
                "created_at": datetime.utcnow()
            }).fetchone()
            
            if not result:
                logger.error("❌ Failed to create ticket")
                return None
            
            # 3. Crea milestone operativa
            milestone_id = self.create_milestone(ticket_id, kit_name)
            if not milestone_id:
                logger.error("❌ Failed to create milestone")
                return None
            
            # 4. Aggiorna ticket con milestone_id
            update_query = text("""
                UPDATE tickets 
                SET milestone_id = :milestone_id, workflow_milestone_id = :workflow_milestone_id
                WHERE id = :ticket_id
            """)
            
            self.db.execute(update_query, {
                "milestone_id": milestone_id,
                "workflow_milestone_id": WORKFLOW_MILESTONE_ID,
                "ticket_id": ticket_id
            })
            
            # 5. Crea task operativi
            tasks_created = self.create_tasks(milestone_id, ticket_id)
            
            # 6. Commit tutto
            self.db.commit()
            
            logger.info(f"🎉 OPERATIONAL TICKET CREATED:")
            logger.info(f"   Ticket ID: {ticket_id}")
            logger.info(f"   Milestone ID: {milestone_id}")
            logger.info(f"   Tasks created: {tasks_created}")
            logger.info(f"   Kit: {kit_name}")
            
            return ticket_id
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error creating operational ticket: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def insert_crm_activity_to_local(self, crm_activity: Dict) -> Optional[int]:
        """Inserisce attività CRM nella tabella activities locale"""
        try:
            # Query CORRETTA per activities (con created_at)
            insert_query = text("""
                INSERT INTO activities (
                    title, description, status, priority, created_at,
                    customer_name, company_id
                ) VALUES (
                    :title, :description, :status, :priority, :created_at,
                    :customer_name, :company_id
                ) RETURNING id
            """)
            
            company_id = None
            if crm_activity.get("companyId"):
                company_id = self.find_company_by_crm_id(crm_activity["companyId"])
            
            result = self.db.execute(insert_query, {
                "title": crm_activity.get("subject", "Attività CRM"),
                "description": crm_activity.get("description", ""),
                "status": "attiva",
                "priority": "media", 
                "created_at": datetime.utcnow(),
                "customer_name": crm_activity.get("customerName", ""),
                "company_id": company_id
            }).fetchone()
            
            local_activity_id = result.id if result else None
            logger.info(f"✅ CRM activity {crm_activity['id']} → local activity {local_activity_id}")
            return local_activity_id
            
        except Exception as e:
            logger.error(f"❌ Error inserting CRM activity: {e}")
            return None
    
    def find_company_by_crm_id(self, crm_company_id: int) -> Optional[int]:
        """Trova company_id nel DB tramite CRM ID"""
        try:
            query = text("SELECT id FROM companies WHERE id = :crm_id")
            result = self.db.execute(query, {"crm_id": str(crm_company_id)}).fetchone()
            return result.id if result else None
        except Exception as e:
            logger.error(f"❌ Error finding company: {e}")
            return None
    
    def sync_operational_activities(self, limit: int = 5) -> Dict[str, int]:
        """
        Sincronizzazione operativa completa
        """
        stats = {
            "activities_checked": 0,
            "intelligence_activities": 0,
            "operational_tickets_created": 0,
            "milestones_created": 0,
            "tasks_created": 0,
            "errors": 0
        }
        
        try:
            # Setup iniziale
            self.get_crm_token()
            self.load_kit_names()
            
            if not self.kit_names:
                logger.warning("⚠️ No kit commerciali found, aborting sync")
                return stats
            
            # Step 1: Ottieni lista ID attività
            activity_ids = self.get_activities_ids(limit)
            stats["activities_checked"] = len(activity_ids)
            
            # Step 2: Processa ogni attività
            for activity_id in activity_ids:
                try:
                    # Ottieni dettaglio attività
                    activity = self.get_activity_detail(activity_id)
                    
                    # Verifica se è di tipo Intelligence
                    if not self.is_intelligence_activity(activity):
                        continue
                        
                    stats["intelligence_activities"] += 1
                    logger.info(f"🔍 Processing Intelligence activity {activity_id}")
                    
                    # Cerca kit nella descrizione
                    description = activity.get("description", "")
                    kit_found = self.find_kit_in_description(description)
                    
                    if not kit_found:
                        logger.info(f"📝 No kit found in activity {activity_id} description")
                        continue
                    
                    # Crea ticket operativo completo
                    ticket_id = self.create_operational_ticket(activity, kit_found)
                    if ticket_id:
                        stats["operational_tickets_created"] += 1
                        stats["milestones_created"] += 1
                        stats["tasks_created"] += len(STANDARD_TASKS)
                        
                except Exception as e:
                    logger.error(f"❌ Error processing activity {activity_id}: {e}")
                    stats["errors"] += 1
                    continue
            
            # Log finale
            logger.info(f"🏁 OPERATIONAL SYNC COMPLETED: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"💥 Fatal error during operational sync: {e}")
            stats["errors"] += 1
            return stats

def main():
    """Test della sincronizzazione operativa"""
    logger.info("🚀 Starting CRM OPERATIONAL Sync...")
    
    with CRMOperationalSync() as sync_service:
        stats = sync_service.sync_operational_activities(limit=3)
        
    logger.info("✨ Operational sync completed!")
    return stats

if __name__ == "__main__":
    main()
