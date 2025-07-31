
#!/usr/bin/env python3
"""
CRM COMMERCIAL SYNC - VERSIONE FINALE DINAMICA AL 100%
Tutto caricato dal database - NIENTE HARDCODE!
"""

import os
import sys
import logging
import uuid
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from sqlalchemy import text

sys.path.append('/var/www/intelligence')
from backend.app.services.crm.activities_sync import CRMSyncService as CRMBaseService
from backend.app.core.database import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crm_commercial_sync")

class CRMCommercialSync(CRMBaseService):
    """Sincronizzatore CRM commerciale - tutto dinamico dal database"""
    
    def __init__(self):
        super().__init__()
        self.db = SessionLocal()
        self.kit_commerciali = {}  # {nome: {"id": id, "codice": codice}}
        self.workflow_config = {}  # Configurazione workflow dal DB
        self.system_user_id = None  # Caricato dal DB
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db:
            self.db.close()
    
    def load_system_config(self):
        """Carica configurazione sistema dal database"""
        try:
            # Carica utente sistema
            user_query = text("SELECT id FROM users WHERE email LIKE '%system%' OR name LIKE '%system%' LIMIT 1")
            user_result = self.db.execute(user_query).fetchone()
            if user_result:
                self.system_user_id = str(user_result.id)
                logger.info(f"📋 Loaded system user: {self.system_user_id}")
            else:
                # Fallback: primo utente disponibile
                fallback_query = text("SELECT id FROM users LIMIT 1")
                fallback_result = self.db.execute(fallback_query).fetchone()
                if fallback_result:
                    self.system_user_id = str(fallback_result.id)
                    logger.info(f"📋 Using fallback user: {self.system_user_id}")
            
            # Carica configurazione workflow milestone più usata
            workflow_query = text("""
                SELECT id, nome FROM workflow_milestones 
                WHERE nome LIKE '%incarico%' OR nome LIKE '%firma%' 
                ORDER BY id 
                LIMIT 1
            """)
            workflow_result = self.db.execute(workflow_query).fetchone()
            if workflow_result:
                self.workflow_config = {
                    "id": workflow_result.id,
                    "nome": workflow_result.nome
                }
                logger.info(f"📋 Loaded workflow: {self.workflow_config['nome']} (ID: {self.workflow_config['id']})")
            
        except Exception as e:
            logger.error(f"❌ Error loading system config: {e}")
    
    def load_kit_commerciali_with_codes(self) -> Dict[str, Dict]:
        """Carica kit commerciali con codici articoli dal database"""
        try:
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
                
            logger.info(f"📦 Loaded {len(self.kit_commerciali)} kit commerciali dinamici")
            return self.kit_commerciali
            
        except Exception as e:
            logger.error(f"❌ Error loading kit commerciali: {e}")
            return {}
    
    def find_kit_in_description(self, description: str) -> Optional[Tuple[str, int, str]]:
        """Trova kit commerciale nella descrizione - ritorna (nome, id, codice)"""
        if not description:
            return None
            
        description_upper = description.upper()
        
        # Match esatto
        for kit_name, kit_data in self.kit_commerciali.items():
            if kit_name.upper() in description_upper:
                logger.info(f"🎯 Found exact kit: {kit_name} → {kit_data['codice']}")
                return (kit_name, kit_data["id"], kit_data["codice"])
        
        # Match parziale
        for kit_name, kit_data in self.kit_commerciali.items():
            kit_words = kit_name.upper().split()
            if len(kit_words) >= 2:
                for i in range(len(kit_words) - 1):
                    partial = " ".join(kit_words[i:i+2])
                    if partial in description_upper:
                        logger.info(f"🎯 Found partial kit: {kit_name} → {kit_data['codice']} via '{partial}'")
                        return (kit_name, kit_data["id"], kit_data["codice"])
        
        return None
    
    def generate_ticket_code(self, codice_articolo: str, crm_activity_id: int) -> str:
        """Genera codice ticket dinamico: TCK-<CODICE>-<4CIFRE>-<SEQ>"""
        try:
            # Ultime 4 cifre CRM activity ID
            activity_suffix = str(crm_activity_id)[-4:].zfill(4)
            
            # Sequenziale: conta ticket esistenti con stesso pattern
            count_query = text("""
                SELECT COUNT(*) as count 
                FROM tickets 
                WHERE ticket_code LIKE :pattern
            """)
            pattern = f"TCK-{codice_articolo}-{activity_suffix}-%"
            count_result = self.db.execute(count_query, {"pattern": pattern}).fetchone()
            sequence = str(count_result.count).zfill(2) if count_result else "00"
            
            ticket_code = f"TCK-{codice_articolo}-{activity_suffix}-{sequence}"
            logger.info(f"🏷️ Generated dynamic ticket code: {ticket_code}")
            return ticket_code
            
        except Exception as e:
            logger.error(f"❌ Error generating ticket code: {e}")
            return f"TCK-GEN-{crm_activity_id}-00"
    
    def get_workflow_tasks_from_db(self, workflow_milestone_id: int) -> List[Dict]:
        """Carica task templates dinamicamente dal database"""
        try:
            # Cerca task esistenti per questo workflow milestone
            query = text("""
                SELECT DISTINCT t.title, t.description, t.ordine, t.sla_giorni
                FROM tasks t
                JOIN milestones m ON t.milestone_id = m.id
                WHERE m.workflow_milestone_id = :workflow_milestone_id
                AND t.title IS NOT NULL
                ORDER BY t.ordine, t.title
                LIMIT 20
            """)
            
            result = self.db.execute(query, {"workflow_milestone_id": workflow_milestone_id}).fetchall()
            
            if result:
                tasks = []
                for i, row in enumerate(result):
                    tasks.append({
                        "title": row.title,
                        "description": row.description or f"Task {row.title}",
                        "ordine": row.ordine or (i + 1),
                        "sla_giorni": row.sla_giorni or 3
                    })
                logger.info(f"📋 Loaded {len(tasks)} task templates from database")
                return tasks
            else:
                logger.warning(f"⚠️ No task templates found for workflow_milestone_id {workflow_milestone_id}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error loading task templates: {e}")
            return []
    
    def create_milestone(self, ticket_id: str, kit_name: str) -> Optional[str]:
        """Crea milestone usando configurazione dinamica"""
        try:
            milestone_id = str(uuid.uuid4())
            
            insert_query = text("""
                INSERT INTO milestones (
                    id, title, descrizione, workflow_milestone_id
                ) VALUES (
                    :id, :title, :descrizione, :workflow_milestone_id
                ) RETURNING id
            """)
            
            result = self.db.execute(insert_query, {
                "id": milestone_id,
                "title": self.workflow_config.get("nome", "Workflow Milestone"),
                "descrizione": f"Milestone per {kit_name}",
                "workflow_milestone_id": self.workflow_config.get("id", 1)
            }).fetchone()
            
            if result:
                logger.info(f"✅ Created dynamic milestone {milestone_id}")
                return milestone_id
            return None
            
        except Exception as e:
            logger.error(f"❌ Error creating milestone: {e}")
            return None
    
    def create_tasks_from_templates(self, milestone_id: str, ticket_id: str, task_templates: List[Dict]) -> int:
        """Crea task dai template dinamici"""
        created_count = 0
        
        try:
            for task_template in task_templates:
                task_id = str(uuid.uuid4())
                
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
                logger.info(f"✅ Created dynamic task: {task_template['title']}")
            
            return created_count
            
        except Exception as e:
            logger.error(f"❌ Error creating tasks: {e}")
            return 0
    
    def create_commercial_ticket(self, activity: Dict, kit_name: str, kit_id: int, codice_articolo: str) -> Optional[str]:
        """Crea ticket commerciale padre completo - tutto dinamico"""
        try:
            # 1. Inserisci attività CRM locale
            local_activity_id = self.insert_crm_activity_to_local(activity)
            if not local_activity_id:
                logger.error(f"❌ Failed to insert CRM activity {activity['id']}")
                return None
            
            # 2. Genera codice ticket dinamico
            ticket_code = self.generate_ticket_code(codice_articolo, activity['id'])
            
            # 3. Crea ticket principale
            ticket_id = str(uuid.uuid4())
            subject = f"[COMMERCIALE] Startoffice Finance - {kit_name}"
            
            description = f"Ticket generato automaticamente da CRM Intelligence.\n\n"
            description += f"🎯 Kit Commerciale: {kit_name}\n"
            description += f"📋 Attività CRM: {activity['id']}\n"
            description += f"🏢 Azienda CRM: {activity.get('companyId', '')}\n\n"
            
            if activity.get("description"):
                description += f"📝 Descrizione originale:\n"
                description += f"{activity['description']}\n\n"
            
            description += f"⚡ Workflow automatico: \"Workflow start\" attivato\n"
            description += f"📌 Milestone: \"{self.workflow_config.get('nome', 'Workflow')}\" con task operativi\n"
            
            # Trova company_id
            company_id = None
            if activity.get("companyId"):
                company_id = self.find_company_by_crm_id(activity["companyId"])
            
            # Metadata dinamico
            metadata = {
                "sync_date": datetime.utcnow().isoformat(),
                "sync_source": "CRM_INTELLIGENCE",
                "crm_company_id": activity.get('companyId'),
                "kit_commerciale": kit_name,
                "kit_commerciale_id": kit_id,
                "codice_articolo": codice_articolo,
                "workflow_instanziato": True
            }
            
            # Crea ticket
            insert_ticket_query = text("""
                INSERT INTO tickets (
                    id, title, description, priority, status, 
                    company_id, activity_id, created_at, created_by,
                    ticket_code, metadata
                ) VALUES (
                    :id, :title, :description, :priority, :status,
                    :company_id, :activity_id, :created_at, :created_by,
                    :ticket_code, :metadata
                ) RETURNING id
            """)
            
            result = self.db.execute(insert_ticket_query, {
                "id": ticket_id,
                "title": subject,
                "description": description,
                "priority": "alta",
                "status": "aperto",
                "company_id": company_id,
                "activity_id": local_activity_id,
                "created_at": datetime.utcnow(),
                "created_by": self.system_user_id,
                "ticket_code": ticket_code,
                "metadata": json.dumps(metadata)
            }).fetchone()
            
            if not result:
                logger.error("❌ Failed to create ticket")
                return None
            
            # 4. Crea milestone dinamica
            milestone_id = self.create_milestone(ticket_id, kit_name)
            if not milestone_id:
                logger.error("❌ Failed to create milestone")
                return None
            
            # 5. Aggiorna ticket con milestone_id
            update_query = text("""
                UPDATE tickets 
                SET milestone_id = :milestone_id, workflow_milestone_id = :workflow_milestone_id
                WHERE id = :ticket_id
            """)
            
            self.db.execute(update_query, {
                "milestone_id": milestone_id,
                "workflow_milestone_id": self.workflow_config.get("id", 1),
                "ticket_id": ticket_id
            })
            
            # 6. Carica task templates dinamici
            task_templates = self.get_workflow_tasks_from_db(self.workflow_config.get("id", 1))
            if not task_templates:
                logger.error("❌ No task templates found")
                return None
            
            # 7. Crea task dinamici
            tasks_created = self.create_tasks_from_templates(milestone_id, ticket_id, task_templates)
            
            # 8. Commit tutto
            self.db.commit()
            
            logger.info(f"🎉 COMMERCIAL TICKET CREATED DINAMICALLY:")
            logger.info(f"   Ticket ID: {ticket_id}")
            logger.info(f"   Ticket Code: {ticket_code}")
            logger.info(f"   Milestone ID: {milestone_id}")
            logger.info(f"   Tasks created: {tasks_created}")
            logger.info(f"   Kit: {kit_name} ({codice_articolo})")
            
            return ticket_id
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error creating commercial ticket: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def insert_crm_activity_to_local(self, crm_activity: Dict) -> Optional[int]:
        """Inserisce attività CRM nella tabella activities locale"""
        try:
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
    
    def sync_commercial_activities(self, limit: int = 5) -> Dict[str, int]:
        """Sincronizzazione commerciale completamente dinamica"""
        stats = {
            "activities_checked": 0,
            "intelligence_activities": 0,
            "kit_found": 0,
            "commercial_tickets_created": 0,
            "milestones_created": 0,
            "tasks_created": 0,
            "errors": 0
        }
        
        try:
            # Setup dinamico
            logger.info("🚀 Starting DYNAMIC CRM Commercial Sync...")
            self.get_crm_token()
            self.load_kit_names()  # Usa metodo base per compatibilità  
            self.load_system_config()  # Carica configurazione dinamica
            self.load_kit_commerciali_with_codes()  # Carica kit con codici
            
            if not self.kit_commerciali:
                logger.warning("⚠️ No kit commerciali found, aborting sync")
                return stats
            
            if not self.workflow_config:
                logger.warning("⚠️ No workflow config found, aborting sync")
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
                    kit_result = self.find_kit_in_description(description)
                    
                    if not kit_result:
                        logger.info(f"📝 No kit found in activity {activity_id} description")
                        continue
                    
                    kit_name, kit_id, codice_articolo = kit_result
                    stats["kit_found"] += 1
                    
                    # Crea ticket commerciale dinamico
                    ticket_id = self.create_commercial_ticket(activity, kit_name, kit_id, codice_articolo)
                    if ticket_id:
                        stats["commercial_tickets_created"] += 1
                        stats["milestones_created"] += 1
                        
                except Exception as e:
                    logger.error(f"❌ Error processing activity {activity_id}: {e}")
                    stats["errors"] += 1
                    continue
            
            # Log finale
            logger.info(f"🏁 DYNAMIC COMMERCIAL SYNC COMPLETED: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"💥 Fatal error during commercial sync: {e}")
            stats["errors"] += 1
            return stats

def main():
    """Test della sincronizzazione commerciale dinamica"""
    logger.info("🚀 Starting DYNAMIC CRM Commercial Sync...")
    
    with CRMCommercialSync() as sync_service:
        stats = sync_service.sync_commercial_activities(limit=3)
        
    logger.info("✨ Dynamic commercial sync completed!")
    return stats

if __name__ == "__main__":
    main()
