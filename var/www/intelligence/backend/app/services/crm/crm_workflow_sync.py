
#!/usr/bin/env python3
"""
CRM Activities Sync - Con Workflow Completo
Crea ticket padre con milestone e task instanziati automaticamente
"""

import sys
sys.path.append('/var/www/intelligence')

import time
import logging
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from uuid import uuid4

from backend.app.core.database import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crm_sync")

# Credenziali CRM
CRM_API_KEY = "r5l50i5lvd.YjuIXg0PPJnqzeldzCBlEpMlwqJPRPFgJppSkPu"
CRM_USERNAME = "intellivoice@enduser-digital.com"
CRM_PASSWORD = "B4b4in4_07"
CRM_BASE_URL = "https://api.crmincloud.it"

CALL_INTERVAL = 60 / 45  # 45 chiamate/minuto
INTELLIGENCE_SUBTYPE_ID = 63705

# Configurazione workflow
DEFAULT_TICKET_TEMPLATE_ID = "7a324655-f0b4-4166-b4ae-ccc6a0d1c738"  # Ticket Start
DEFAULT_WORKFLOW_TEMPLATE_ID = 1  # Workflow start
DEFAULT_MILESTONE_ID = 3  # invio incarico in firma  # Workflow start

class CRMWorkflowSync:
    def __init__(self):
        self.db = SessionLocal()
        self.token = None
        self.headers = None
        self.kit_names = []
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()
        
    def get_crm_token(self) -> str:
        """Ottieni token CRM"""
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
        
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        self.token = response.json()["access_token"]
        self.headers = {
            "Authorization": f"Bearer {self.token}", 
            "WebApiKey": CRM_API_KEY
        }
        
        logger.info("✅ CRM token obtained")
        return self.token
    
    def rate_limited_request(self, url: str) -> requests.Response:
        """Richiesta con rate limiting"""
        time.sleep(CALL_INTERVAL)
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response
    
    def load_kit_names(self) -> List[str]:
        """Carica nomi kit dal DB"""
        query = text("SELECT nome FROM kit_commerciali WHERE attivo = true")
        result = self.db.execute(query).fetchall()
        self.kit_names = [row.nome for row in result]
        logger.info(f"📦 Loaded {len(self.kit_names)} kit names")
        return self.kit_names
    
    def find_kit_in_description(self, description: str) -> Optional[str]:
        """Cerca kit nella descrizione"""
        if not description:
            return None
            
        desc_upper = description.upper()
        
        # Match esatto
        for kit_name in self.kit_names:
            if kit_name.upper() in desc_upper:
                return kit_name
                
        # Match parziale (2+ parole consecutive)
        for kit_name in self.kit_names:
            words = kit_name.upper().split()
            if len(words) >= 2:
                for i in range(len(words) - 1):
                    partial = " ".join(words[i:i+2])
                    if partial in desc_upper:
                        return kit_name
        return None
    
    def activity_already_processed(self, activity_id: int) -> bool:
        """Verifica se attività già processata usando metadata"""
        query = text("""
            SELECT id FROM tickets 
            WHERE metadata::jsonb ->> 'crm_activity_id' = :activity_id
        """)
        result = self.db.execute(query, {"activity_id": str(activity_id)}).fetchone()
        return result is not None
    
    def find_company_by_crm_id(self, crm_company_id: int) -> Optional[int]:
        """Trova company tramite CRM ID"""
        query = text("SELECT id FROM companies WHERE id = :company_id")
        result = self.db.execute(query, {"company_id": crm_company_id}).fetchone()
        if result:
            logger.info(f"✅ Found company {result.id} for CRM ID {crm_company_id}")
            return result.id
        else:
            logger.warning(f"⚠️ Company not found for CRM ID {crm_company_id}")
            return None
    
    def create_milestone_instance(self, ticket_id: str, milestone_template: Dict) -> str:
        """Crea istanza di milestone per il ticket"""
        milestone_id = str(uuid4())
        
        # Calcola SLA (7 giorni lavorativi di default)
        sla_deadline = datetime.utcnow() + timedelta(days=7)
        
        insert_query = text("""
            INSERT INTO milestones (
                id, title, descrizione, stato, 
                data_inizio, data_fine_prevista, sla_hours,
                workflow_milestone_id, created_by
            ) VALUES (
                :id, :title, :descrizione, :stato,
                :data_inizio, :data_fine_prevista, :sla_hours,
                :workflow_milestone_id, :created_by
            )
        """)
        
        self.db.execute(insert_query, {
            "id": milestone_id,
            "title": milestone_template["nome"],
            "descrizione": milestone_template["descrizione"],
            "stato": "pianificata",
            "data_inizio": datetime.utcnow(),
            "data_fine_prevista": sla_deadline,
            "sla_hours": 168,  # 7 giorni * 24 ore
            "workflow_milestone_id": milestone_template["id"],
            "created_by": "crm_sync"
        })
        
        # Ora aggiorna il ticket per collegarlo alla milestone
        update_ticket_query = text("""
            UPDATE tickets 
            SET milestone_id = :milestone_id 
            WHERE id = :ticket_id
        """)
        
        self.db.execute(update_ticket_query, {
            "milestone_id": milestone_id,
            "ticket_id": ticket_id
        })
        
        logger.info(f"✅ Created milestone instance: {milestone_template['nome']}")
        return milestone_id
    
    def create_task_instance(self, milestone_id: str, task_template: Dict) -> str:
        """Crea istanza di task per la milestone"""
        task_id = str(uuid4())
        
        # Calcola SLA task (durata_stimata_ore convertita in giorni)
        ore_stimate = task_template.get("durata_stimata_ore", 8)
        giorni_stimate = max(1, (ore_stimate + 7) // 8)  # Arrotonda per eccesso
        sla_deadline = datetime.utcnow() + timedelta(days=giorni_stimate)
        
        insert_query = text("""
            INSERT INTO tasks (
                id, milestone_id, title, description, status,
                sla_deadline, estimated_hours, sla_hours, created_at,
                task_template_id, priorita, ordine
            ) VALUES (
                :id, :milestone_id, :title, :description, :status,
                :sla_deadline, :estimated_hours, :sla_hours, :created_at,
                :task_template_id, :priorita, :ordine
            )
        """)
        
        self.db.execute(insert_query, {
            "id": task_id,
            "milestone_id": milestone_id,
            "title": task_template["nome"],
            "description": task_template["descrizione"],
            "status": "todo",  # Usa 'todo' invece di 'da_iniziare'
            "sla_deadline": sla_deadline,
            "estimated_hours": ore_stimate,
            "sla_hours": ore_stimate,
            "created_at": datetime.utcnow(),
            "created_by": owner_user_id,
            "task_template_id": task_template.get("id"),
            "priorita": "normale",
            "ordine": task_template.get("ordine", 0)
        })
        
        logger.info(f"   ✅ Created task: {task_template['nome']} ({ore_stimate}h)")
        return task_id
    
    def get_workflow_structure(self, workflow_id: int) -> List[Dict]:
        """Ottieni struttura completa del workflow (milestone + task)"""
        query = text("""
            SELECT 
                wm.id, wm.nome, wm.descrizione, wm.ordine,
                mtt.id as task_id, mtt.nome as task_nome, 
                mtt.descrizione as task_descrizione, mtt.ordine as task_ordine,
                mtt.durata_stimata_ore
            FROM workflow_milestones wm
            LEFT JOIN milestone_task_templates mtt ON wm.id = mtt.milestone_id
            WHERE wm.workflow_template_id = :workflow_id
            ORDER BY wm.ordine, mtt.ordine
        """)
        
        result = self.db.execute(query, {"workflow_id": workflow_id}).fetchall()
        
        # Raggruppa per milestone
        milestones = {}
        for row in result:
            milestone_id = row.id
            if milestone_id not in milestones:
                milestones[milestone_id] = {
                    "id": row.id,
                    "nome": row.nome,
                    "descrizione": row.descrizione,
                    "ordine": row.ordine,
                    "tasks": []
                }
            
            if row.task_id:  # Ha task associati
                milestones[milestone_id]["tasks"].append({
                    "id": row.task_id,
                    "nome": row.task_nome,
                    "descrizione": row.task_descrizione,
                    "ordine": row.task_ordine,
                    "durata_stimata_ore": row.durata_stimata_ore
                })
        
        return list(milestones.values())
    
    def create_ticket_with_workflow(self, activity: Dict, kit_name: str) -> Optional[str]:
        """Crea ticket padre con workflow completo instanziato"""
        try:
            activity_id = activity["id"]
            
            # Check duplicati
            if self.activity_already_processed(activity_id):
                logger.info(f"⏭️ Activity {activity_id} already processed")
                return None
            
            # Trova company
            company_id = None
            if activity.get("companyId"):
                company_id = self.find_company_by_crm_id(activity["companyId"])
            
            # Prepara dati ticket
            
            # Trova responsabile dal kit commerciale
            owner_user_id = None
            try:
                from app.models.kit_commerciali import KitCommerciale, KitArticolo
                from app.models.articoli import Articolo
                
                kit = self.db.query(KitCommerciale).filter(
                    KitCommerciale.nome.ilike(f"%{kit_name}%")
                ).first()
                
                if kit:
                    # Prendi il primo articolo con responsabile
                    kit_articolo = self.db.query(KitArticolo).join(Articolo).filter(
                        KitArticolo.kit_commerciale_id == kit.id,
                        Articolo.responsabile_user_id.isnot(None)
                    ).first()
                    
                    if kit_articolo and kit_articolo.articolo:
                        owner_user_id = kit_articolo.articolo.responsabile_user_id
                        
            except Exception as e:
                logger.warning(f"Could not find kit owner: {e}")
            ticket_id = str(uuid4())
            title = f"Richiesta Commerciale - {kit_name}"
            if activity.get("subject"):
                title = f"{activity['subject']} - {kit_name}"
            
            description = f"""Ticket generato automaticamente da CRM Intelligence.

🎯 Kit Commerciale: {kit_name}
📋 Attività CRM: {activity_id}
🏢 Azienda CRM: {activity.get('companyId', 'N/A')}

📝 Descrizione originale:
{activity.get('description', '')}

⚡ Workflow automatico: "Workflow start" attivato
📌 Milestone: "invio incarico in firma" con 4 task operativi
"""
            
            # Metadata con info kit
            metadata = {
                "kit_commerciale": kit_name,
                "crm_company_id": activity.get("companyId"),
                "workflow_instanziato": True,
                "sync_source": "CRM_INTELLIGENCE",
                "sync_date": datetime.utcnow().isoformat()
            }
            
            # 1. Crea ticket padre
            insert_ticket_query = text("""
                INSERT INTO tickets (
                    id, title, description, status, priority, company_id,
                    workflow_milestone_id, modello_ticket_id, metadata, 
                    created_at, created_by
                ) VALUES (
                    :id, :title, :description, :status, :priority, :company_id,
                    :workflow_milestone_id, :modello_ticket_id, :metadata, 
                    :created_at, :created_by
                )
            """)
            
            self.db.execute(insert_ticket_query, {
                "id": ticket_id,
                "title": title,
                "description": description,
                "status": "aperto",
                "priority": "alta",
                "company_id": company_id,
                "modello_ticket_id": DEFAULT_TICKET_TEMPLATE_ID,
                "workflow_milestone_id": DEFAULT_MILESTONE_ID,
                "metadata": json.dumps(metadata),
                "created_at": datetime.utcnow(),
            "created_by": owner_user_id,
            })
            
            logger.info(f"✅ Created ticket {ticket_id} for kit '{kit_name}'")
            
            # 2. Instanzia workflow (milestone + task)
            workflow_structure = self.get_workflow_structure(DEFAULT_WORKFLOW_TEMPLATE_ID)
            
            for milestone_template in workflow_structure:
                # Crea milestone
                milestone_id = self.create_milestone_instance(ticket_id, milestone_template)
                
                # Crea task della milestone
                for task_template in milestone_template["tasks"]:
                    self.create_task_instance(milestone_id, task_template)
            
            self.db.commit()
            logger.info(f"🎯 Workflow instanziato per ticket {ticket_id}")
            return ticket_id
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error creating ticket with workflow: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def sync_activities(self, limit: int = 10) -> Dict[str, int]:
        """Sincronizzazione principale"""
        stats = {
            "activities_checked": 0,
            "intelligence_activities": 0,
            "tickets_created": 0,
            "workflows_instantiated": 0,
            "errors": 0
        }
        
        try:
            # Setup
            self.get_crm_token()
            self.load_kit_names()
            
            # Get activities
            url = f"{CRM_BASE_URL}/api/v1/Activities?limit=100"
            response = self.rate_limited_request(url)
            activity_ids = response.json()[:limit]
            
            stats["activities_checked"] = len(activity_ids)
            logger.info(f"📊 Processing {len(activity_ids)} activities...")
            
            # Process activities
            for activity_id in activity_ids:
                try:
                    # Get detail
                    detail_url = f"{CRM_BASE_URL}/api/v1/Activities/{activity_id}"
                    activity = self.rate_limited_request(detail_url).json()
                    
                    # Check Intelligence type
                    if activity.get("subTypeId") != INTELLIGENCE_SUBTYPE_ID:
                        continue
                        
                    stats["intelligence_activities"] += 1
                    logger.info(f"🔍 Processing Intelligence activity {activity_id}")
                    
                    # Find kit
                    description = activity.get("description", "")
                    kit_found = self.find_kit_in_description(description)
                    
                    if not kit_found:
                        logger.info(f"📝 No kit found in activity {activity_id}")
                        continue
                    
                    # Create ticket with workflow
                    ticket_id = self.create_ticket_with_workflow(activity, kit_found)
                    if ticket_id:
                        stats["tickets_created"] += 1
                        stats["workflows_instantiated"] += 1
                        
                except Exception as e:
                    logger.error(f"❌ Error processing activity {activity_id}: {e}")
                    stats["errors"] += 1
            
            logger.info(f"🏁 Sync completed: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"💥 Fatal sync error: {e}")
            stats["errors"] += 1
            return stats

def main():
    """Test del sincronizzatore con workflow"""
    print("🚀 Starting CRM Sync with Workflow...")
    
    with CRMWorkflowSync() as sync:
        stats = sync.sync_activities(limit=5)  # Test con 5 attività
        
    print(f"✨ Completed: {stats}")

if __name__ == "__main__":
    main()
