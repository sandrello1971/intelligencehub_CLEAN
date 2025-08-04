#!/usr/bin/env python3
"""
Workflow Generator - Modulo 2
Genera il flusso operativo completo dall'attività CRM
"""

import os
import logging
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from uuid import uuid4

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("workflow_generator")

class WorkflowGenerator:
    """
    Generatore del flusso operativo completo dall'attività CRM
    """
    
    def __init__(self, database_session: Session):
        self.db = database_session
    
    def extract_kit_from_description(self, description: str, title: str = "") -> Optional[str]:
        """
        Estrae il kit commerciale dalla descrizione dell'attività
        """
        full_text = f"{title} {description}".lower()
        
        kit_patterns = {
            "Kit Start Office Finance": [
                "start office finance", "startoffice finance", 
                "sof", "start office fin"
            ],
            "Kit Start Office Digital": [
                "start office digital", "startoffice digital", 
                "sod"
            ],
            "Kit Start Office Training": [
                "start office training", "startoffice training", 
                "sot"
            ],
            "Kit Start Office Sustainability": [
                "start office sustainability", "startoffice sustainability", 
                "sos"
            ],
            "Kit Incarico 24 Mesi": [
                "incarico 24 mesi", "i24", "24 mesi"
            ],
            "Kit Incarico Consulenza Strumenti Economico- Finanziari": [
                "consulenza strumenti", "ics", "strumenti economico"
            ]
        }
        
        logger.info(f"🔍 Analizzando: '{full_text[:100]}'")
        
        for kit_name, patterns in kit_patterns.items():
            for pattern in patterns:
                if pattern in full_text:
                    logger.info(f"🎯 Kit identificato: {kit_name} via pattern '{pattern}'")
                    return kit_name
        
        logger.warning(f"⚠️ Nessun kit identificato da: '{full_text[:100]}'")
        return None
    
    def find_kit_details(self, kit_name: str) -> Optional[Dict]:
        query = text("""
            SELECT k.id, k.nome, k.descrizione, 
                   a.id as articolo_id, a.nome as articolo_nome, 
                   a.codice, a.responsabile_user_id
            FROM kit_commerciali k
            LEFT JOIN articoli a ON k.articolo_principale_id = a.id
            WHERE k.nome = :kit_name AND k.attivo = true
            LIMIT 1
        """)
        
        result = self.db.execute(query, {"kit_name": kit_name}).fetchone()
        
        if result:
            return {
                "id": result.id,
                "nome": result.nome,
                "descrizione": result.descrizione,
                "articolo_id": result.articolo_id,
                "articolo_nome": result.articolo_nome,
                "codice": result.codice,
                "responsabile_user_id": result.responsabile_user_id
            }
        return None
    
    def find_user_by_crm_id(self, crm_id: str) -> Optional[Dict]:
        query = text("""
            SELECT id, name, surname, email, role, crm_id
            FROM users 
            WHERE crm_id = :crm_id
            LIMIT 1
        """)
        
        result = self.db.execute(query, {"crm_id": str(crm_id)}).fetchone()
        
        if result:
            return {
                "id": result.id,
                "name": result.name,
                "surname": result.surname,
                "email": result.email,
                "role": result.role,
                "crm_id": result.crm_id,
                "full_name": f"{result.name} {result.surname}".strip()
            }
        return None
    
    def get_default_workflow(self) -> Optional[Dict]:
        query = text("""
            SELECT id, nome, descrizione, wkf_code
            FROM workflow_templates 
            WHERE nome = 'Workflow start' AND attivo = true
            LIMIT 1
        """)
        
        result = self.db.execute(query).fetchone()
        
        if result:
            return {
                "id": result.id,
                "nome": result.nome,
                "descrizione": result.descrizione,
                "wkf_code": result.wkf_code
            }
        return None
    
    def get_workflow_milestones(self, workflow_id: int) -> List[Dict]:
        query = text("""
            SELECT id, nome, descrizione, ordine, sla_giorni, warning_giorni
            FROM workflow_milestones 
            WHERE workflow_template_id = :workflow_id
            ORDER BY ordine
        """)
        
        results = self.db.execute(query, {"workflow_id": workflow_id}).fetchall()
        
        milestones = []
        for result in results:
            milestones.append({
                "id": result.id,
                "nome": result.nome,
                "descrizione": result.descrizione,
                "ordine": result.ordine,
                "sla_giorni": result.sla_giorni,
                "warning_giorni": result.warning_giorni
            })
        
        return milestones
    
    def get_milestone_tasks(self, milestone_id: int) -> List[Dict]:
        query = text("""
            SELECT id, nome, descrizione, ordine, durata_stimata_ore, 
                   ruolo_responsabile, obbligatorio, tipo_task
            FROM milestone_task_templates 
            WHERE milestone_id = :milestone_id
            ORDER BY ordine
        """)
        
        results = self.db.execute(query, {"milestone_id": milestone_id}).fetchall()
        
        tasks = []
        for result in results:
            tasks.append({
                "id": result.id,
                "nome": result.nome,
                "descrizione": result.descrizione,
                "ordine": result.ordine,
                "durata_stimata_ore": result.durata_stimata_ore,
                "ruolo_responsabile": result.ruolo_responsabile,
                "obbligatorio": result.obbligatorio,
                "tipo_task": result.tipo_task
            })
        
        return tasks
    
    def create_ticket(self, activity_id: int, kit_details: Dict, user_details: Dict, 
                     workflow_details: Dict) -> Optional[str]:
        try:
            ticket_id = str(uuid4())
            
            activity_query = text("""
                SELECT a.title, a.description, a.customer_name, a.customer_id, a.company_id, a.crm_activity_id,
                       COALESCE(a.customer_name, c.name) as resolved_customer_name
                FROM activities a
                LEFT JOIN companies c ON c.id = a.customer_id::bigint
                WHERE a.id = :activity_id
            """)
            activity = self.db.execute(activity_query, {"activity_id": activity_id}).fetchone()
            
            if not activity:
                logger.error(f"❌ Attività {activity_id} non trovata")
                return None
            
            title = f"{kit_details['nome']} - {activity.resolved_customer_name or 'Cliente'}"
            description = f"""Ticket generato automaticamente da CRM Intelligence

🎯 Kit Commerciale: {kit_details['nome']}
📋 Servizio: {kit_details['articolo_nome']} ({kit_details['codice']})
🏢 Cliente: {activity.resolved_customer_name or 'N/A'}
👤 Account Manager: {user_details['full_name']}
⚡ Workflow: {workflow_details['nome']}

📝 Descrizione originale:
{activity.description or ''}

🔄 Workflow automatico attivato con milestone e task operativi.
"""
            
            ticket_code = f"TCK-{kit_details["codice"]}-{str(activity.crm_activity_id)[-4:]}-00"
            
            insert_query = text("""
                INSERT INTO tickets (
                    id, title, description, status, priority,
                    activity_id, company_id, assigned_to, created_by,
                    articolo_id, ticket_code, due_date, created_at, updated_at
                ) VALUES (
                    :id, :title, :description, :status, :priority,
                    :activity_id, :company_id, :assigned_to, :created_by,
                    :articolo_id, :ticket_code, :due_date, :created_at, :updated_at
                ) RETURNING id
            """)
            
            result = self.db.execute(insert_query, {
                "id": ticket_id,
                "title": title,
                "description": description,
                "status": "aperto",
                "priority": "media",
                "activity_id": activity_id,
                "company_id": activity.customer_id,
                "assigned_to": kit_details.get("responsabile_user_id") or user_details["id"],
                "created_by": user_details['id'],
                "articolo_id": kit_details['articolo_id'],
                "ticket_code": ticket_code,
                "due_date": datetime.utcnow() + timedelta(days=7),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }).fetchone()
            
            logger.info(f"✅ Ticket creato: {ticket_id} - {title}")
            return ticket_id
            
        except Exception as e:
            logger.error(f"❌ Errore creazione ticket: {e}")
            return None
    
    def create_milestone_instance(self, ticket_id: str, milestone_template: Dict) -> Optional[str]:
        """
        Crea una milestone reale (UUID) nella tabella milestones
        """
        try:
            milestone_id = str(uuid4())
            
            insert_query = text("""
                INSERT INTO milestones (
                    id, title, descrizione, stato, 
                    data_inizio, data_fine_prevista,
                    workflow_milestone_id, sla_hours, 
                    warning_days, escalation_days, auto_generate_tickets
                ) VALUES (
                    :id, :title, :descrizione, :stato,
                    :data_inizio, :data_fine_prevista, 
                    :workflow_milestone_id, :sla_hours,
                    :warning_days, :escalation_days, :auto_generate_tickets
                ) RETURNING id
            """)
            
            self.db.execute(insert_query, {
                "id": milestone_id,
                "title": milestone_template['nome'],
                "descrizione": milestone_template.get('descrizione', ''),
                "stato": "pianificata",
                "data_inizio": datetime.utcnow(),
                "data_fine_prevista": datetime.utcnow() + timedelta(days=milestone_template.get('sla_giorni', 5)),
                "workflow_milestone_id": milestone_template['id'],
                "sla_hours": milestone_template.get('sla_giorni', 5) * 24,
                "warning_days": milestone_template.get('warning_giorni', 2),
                "escalation_days": 1,
                "auto_generate_tickets": True
            })
            
            update_query = text("""
                UPDATE tickets 
                SET milestone_id = CAST(:milestone_id AS uuid),
                    workflow_milestone_id = :workflow_milestone_id
                WHERE id = CAST(:ticket_id AS uuid)
            """)
            
            self.db.execute(update_query, {
                "milestone_id": milestone_id,
                "workflow_milestone_id": milestone_template['id'],
                "ticket_id": ticket_id
            })
            
            logger.info(f"✅ Milestone creata: {milestone_id} - {milestone_template['nome']}")
            return milestone_id
            
        except Exception as e:
            logger.error(f"❌ Errore creazione milestone: {e}")
            return None
    
    def create_task_instances(self, ticket_id: str, milestone_id: str, 
                            task_templates: List[Dict], owner_id: str) -> List[str]:
        created_tasks = []
        
        for task_template in task_templates:
            try:
                task_id = str(uuid4())
                
                due_date = datetime.utcnow().date() + timedelta(
                    days=task_template.get('durata_stimata_ore', 8) // 24 or 1
                )
                
                insert_query = text("""
                    INSERT INTO tasks (
                        id, title, description, status, 
                        ticket_id, milestone_id, assigned_to,
                        created_at, due_date, estimated_hours, 
                        ordine, priorita, task_template_id
                    ) VALUES (
                        :id, :title, :description, :status,
                        CAST(:ticket_id AS uuid), CAST(:milestone_id AS uuid), CAST(:assigned_to AS uuid),
                        :created_at, :due_date, :estimated_hours,
                        :ordine, :priorita, :task_template_id
                    ) RETURNING id
                """)
                
                self.db.execute(insert_query, {
                    "id": task_id,
                    "title": task_template['nome'],
                    "description": task_template.get('descrizione', ''),
                    "status": "todo",
                    "ticket_id": ticket_id,
                    "milestone_id": milestone_id,
                    "assigned_to": owner_id,
                    "created_at": datetime.utcnow(),
                    "due_date": due_date,
                    "estimated_hours": task_template.get('durata_stimata_ore', 8),
                    "ordine": task_template.get('ordine', 0),
                    "priorita": "normale",
                    "task_template_id": task_template['id']
                })
                
                created_tasks.append(task_id)
                logger.info(f"✅ Task creato: {task_template['nome']} (ID: {task_id})")
                
            except Exception as e:
                logger.error(f"❌ Errore creazione task {task_template['nome']}: {e}")
                continue
        
        return created_tasks

    def generate_workflow_from_activity(self, activity_id: int) -> Dict:
        stats = {
            "activity_id": activity_id,
            "success": False,
            "kit_identificato": None,
            "ticket_creato": None,
            "milestones_create": 0,
            "tasks_creati": 0,
            "errori": []
        }
        
        try:
            activity_query = text("""
                SELECT id, title, description, owner_id, customer_name, customer_id, company_id
                FROM activities 
                WHERE id = :activity_id
            """)
            activity = self.db.execute(activity_query, {"activity_id": activity_id}).fetchone()
            
            if not activity:
                stats["errori"].append("Attività non trovata")
                return stats
            
            kit_name = self.extract_kit_from_description(
                activity.description or "", 
                activity.title or ""
            )
            
            if not kit_name:
                stats["errori"].append("Kit commerciale non identificato")
                return stats
            
            stats["kit_identificato"] = kit_name
            
            kit_details = self.find_kit_details(kit_name)
            if not kit_details:
                stats["errori"].append(f"Dettagli kit '{kit_name}' non trovati")
                return stats
            
            user_details = self.find_user_by_crm_id(activity.owner_id)
            if not user_details:
                if kit_details.get('responsabile_user_id'):
                    user_query = text("""
                        SELECT id, name, surname, email, role
                        FROM users WHERE id = :user_id
                    """)
                    user_result = self.db.execute(user_query, {
                        "user_id": kit_details['responsabile_user_id']
                    }).fetchone()
                    
                    if user_result:
                        user_details = {
                            "id": user_result.id,
                            "name": user_result.name,
                            "surname": user_result.surname,
                            "email": user_result.email,
                            "role": user_result.role,
                            "full_name": f"{user_result.name} {user_result.surname}".strip()
                        }
            
            if not user_details:
                stats["errori"].append(f"Account manager CRM {activity.owner_id} non trovato")
                return stats
            
            workflow_details = self.get_default_workflow()
            if not workflow_details:
                stats["errori"].append("Workflow di default non trovato")
                return stats
            
            ticket_id = self.create_ticket(activity_id, kit_details, user_details, workflow_details)
            if not ticket_id:
                stats["errori"].append("Errore creazione ticket")
                return stats
            
            stats["ticket_creato"] = ticket_id
            
            milestones = self.get_workflow_milestones(workflow_details['id'])
            if not milestones:
                stats["errori"].append("Nessuna milestone trovata per il workflow")
                return stats
            
            first_milestone = milestones[0]
            milestone_id = self.create_milestone_instance(ticket_id, first_milestone)
            
            if milestone_id:
                stats["milestones_create"] = 1
                
                task_templates = self.get_milestone_tasks(first_milestone['id'])
                if task_templates:
                    created_tasks = self.create_task_instances(
                        ticket_id, milestone_id, task_templates, user_details['id']
                    )
                    stats["tasks_creati"] = len(created_tasks)
            
            self.db.commit()
            stats["success"] = True
            
            logger.info(f"🎉 Workflow generato con successo: {stats}")
            
        except Exception as e:
            logger.error(f"❌ Errore critico generazione workflow: {e}")
            self.db.rollback()
            stats["errori"].append(f"Errore critico: {e}")
        
        return stats


def generate_workflow_for_activity(activity_id: int) -> Dict:
    try:
        from app.core.database import SessionLocal
    except ImportError:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        DATABASE_URL = "postgresql://intelligence_user:intelligence_pass@localhost/intelligence"
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    
    try:
        generator = WorkflowGenerator(db)
        return generator.generate_workflow_from_activity(activity_id)
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python workflow_generator.py <activity_id>")
        sys.exit(1)
    
    activity_id = int(sys.argv[1])
    print(f"🚀 Generazione workflow per attività {activity_id}")
    
    result = generate_workflow_for_activity(activity_id)
    print(f"📊 Risultato: {result}")
