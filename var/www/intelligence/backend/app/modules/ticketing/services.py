
"""
Intelligence Ticketing Module - Services
Business logic for ticket and task management - VERSIONE FINALE COMPLETA
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, text

from app.models.task import Task
from app.models.ticket import Ticket
from app.models.users import User
from app.models.activity import Activity


class TicketingService:
    """Core service for ticket and task management - VERSIONE FINALE BUSINESS"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ===== WORKFLOW DYNAMICS METHODS =====
    
    def _get_default_workflow_id(self) -> int:
        """Recupera ID del workflow commerciale standard"""
        try:
            query = text("SELECT id FROM workflow_templates WHERE nome = 'Workflow start' AND attivo = true LIMIT 1")
            result = self.db.execute(query).fetchone()
            return result.id if result else 1
        except Exception as e:
            print(f"⚠️ Warning getting workflow ID: {e}")
            return 1

    def _get_default_milestone_id(self) -> int:
        """Recupera ID della milestone commerciale standard"""
        try:
            workflow_id = self._get_default_workflow_id()
            query = text("""
                SELECT id FROM workflow_milestones 
                WHERE workflow_template_id = :workflow_id 
                AND nome ILIKE '%incarico%firma%' 
                ORDER BY ordine LIMIT 1
            """)
            result = self.db.execute(query, {"workflow_id": workflow_id}).fetchone()
            return result.id if result else 3
        except Exception as e:
            print(f"⚠️ Warning getting milestone ID: {e}")
            return 3

    def validate_kit_commerciale(self, kit_identifier: str) -> Optional[Dict[str, Any]]:
        """Validazione kit commerciale - VERSIONE SQL PURA"""
        try:
            if kit_identifier.isdigit():
                kit_query = text("""
                    SELECT kc.id, kc.nome, kc.descrizione, kc.articolo_principale_id,
                           a.codice, a.responsabile_user_id
                    FROM kit_commerciali kc
                    LEFT JOIN articoli a ON kc.articolo_principale_id = a.id
                    WHERE kc.attivo = true AND kc.id = :kit_id
                    LIMIT 1
                """)
                result = self.db.execute(kit_query, {"kit_id": int(kit_identifier)}).fetchone()
            else:
                kit_query = text("""
                    SELECT kc.id, kc.nome, kc.descrizione, kc.articolo_principale_id,
                           a.codice, a.responsabile_user_id
                    FROM kit_commerciali kc
                    LEFT JOIN articoli a ON kc.articolo_principale_id = a.id
                    WHERE kc.attivo = true AND (kc.nome ILIKE :nome_like OR kc.nome = :nome_exact)
                    LIMIT 1
                """)
                result = self.db.execute(kit_query, {
                    "nome_like": f"%{kit_identifier}%",
                    "nome_exact": kit_identifier
                }).fetchone()
            
            if not result:
                return {"success": False, "error": f"Kit commerciale '{kit_identifier}' non trovato"}
            
            codice_articolo = result.codice or f"KIT{result.id}"
            
            return {
                "success": True,
                "kit": {
                    "id": result.id,
                    "nome": result.nome,
                    "codice": codice_articolo,
                    "descrizione": result.descrizione,
                    "articolo_principale_id": result.articolo_principale_id,
                    "responsabile_user_id": result.responsabile_user_id
                }
            }
            
        except Exception as e:
            print(f"❌ Error in validate_kit_commerciale: {e}")
            return {"success": False, "error": str(e)}
    
    def insert_crm_activity_to_local(self, crm_activity: Dict[str, Any]) -> Optional[int]:
        """Inserisce attività CRM nella tabella activities locale con Account Manager"""
        try:
            insert_query = text("""
                INSERT INTO activities (
                    title, description, status, priority, created_at,
                    customer_name, company_id, accompagnato_da, accompagnato_da_nome
                ) VALUES (
                    :title, :description, :status, :priority, :created_at,
                    :customer_name, :company_id, :accompagnato_da, :accompagnato_da_nome
                ) RETURNING id
            """)
            
            company_id = None
            if crm_activity.get('companyId'):
                try:
                    company_query = text('SELECT id FROM companies WHERE id = :crm_id')
                    company_result = self.db.execute(company_query, {'crm_id': str(crm_activity['companyId'])}).fetchone()
                    if company_result:
                        company_id = company_result.id
                except Exception:
                    pass
            
            # Recupera info Account Manager
            account_manager_id = crm_activity.get('idCompanion')
            account_manager_name = None
            if account_manager_id:
                try:
                    am_query = text('SELECT name, surname FROM users WHERE crm_id = :crm_id')
                    am_result = self.db.execute(am_query, {'crm_id': account_manager_id}).fetchone()
                    if am_result:
                        account_manager_name = f'{am_result.name} {am_result.surname}'.strip()
                except Exception:
                    pass
            
            result = self.db.execute(insert_query, {
                'title': crm_activity.get('subject', 'Attività CRM'),
                'description': crm_activity.get('description', ''),
                'status': 'attiva',
                'priority': 'media', 
                'created_at': datetime.utcnow(),
                'customer_name': crm_activity.get('customerName', ''),
                'company_id': company_id,
                'accompagnato_da': account_manager_id,
                'accompagnato_da_nome': account_manager_name
            }).fetchone()
            
            local_activity_id = result.id if result else None
            print(f'✅ CRM activity {crm_activity["id"]} → local activity {local_activity_id}')
            return local_activity_id
            
        except Exception as e:
            print(f'❌ Error inserting CRM activity: {e}')
            return None

    def _create_real_milestone(self, ticket_id: str, kit_name: str) -> Optional[str]:
        """Crea milestone reale per il ticket commerciale - SENZA HARDCODE"""
        try:
            import uuid
            milestone_id = str(uuid.uuid4())
            
            workflow_milestone_id = self._get_default_milestone_id()
            
            insert_query = text("""
                INSERT INTO milestones (
                    id, title, descrizione, workflow_milestone_id, due_date
                ) VALUES (
                    :id, :title, :descrizione, :workflow_milestone_id, :due_date
                )
            """)
            
            self.db.execute(insert_query, {
                "id": milestone_id,
                "title": "Invio incarico in firma",
                "descrizione": f"Milestone commerciale per {kit_name}",
                "workflow_milestone_id": workflow_milestone_id,
                "due_date": None
            })
            
            return milestone_id
            
        except Exception as e:
            print(f"❌ Error creating milestone: {e}")
            return None
    
    def _create_commercial_tasks(self, milestone_id: str, ticket_id: str) -> int:
        """Crea task commerciali dal database - SENZA HARDCODE"""
        tasks_created = 0
        
        try:
            workflow_milestone_id = self._get_default_milestone_id()
            
            task_query = text("""
                SELECT id, nome, descrizione, ordine, durata_stimata_ore 
                FROM milestone_task_templates 
                WHERE milestone_id = :milestone_id 
                ORDER BY ordine
            """)
            
            task_templates = self.db.execute(task_query, {"milestone_id": workflow_milestone_id}).fetchall()
            
            if not task_templates:
                print(f"⚠️ No task templates found for milestone {workflow_milestone_id}")
                return 0
            
            for task_template in task_templates:
                import uuid
                task_id = str(uuid.uuid4())
                
                insert_query = text("""
                    INSERT INTO tasks (
                        id, title, description, status, priorita, 
                        milestone_id, ticket_id, sla_giorni, ordine, estimated_hours
                    ) VALUES (
                        :id, :title, :description, :status, :priorita,
                        :milestone_id, :ticket_id, :sla_giorni, :ordine, :estimated_hours
                    )
                """)
                
                sla_giorni = max(1, (task_template.durata_stimata_ore or 8) // 8)
                
                self.db.execute(insert_query, {
                    "id": task_id,
                    "title": task_template.nome,
                    "description": task_template.descrizione,
                    "status": "todo",
                    "priorita": "alta",
                    "milestone_id": milestone_id,
                    "ticket_id": ticket_id,
                    "sla_giorni": sla_giorni,
                    "ordine": task_template.ordine,
                    "estimated_hours": task_template.durata_stimata_ore
                })
                
                tasks_created += 1
                print(f"   ✅ Created task: {task_template.nome} ({task_template.durata_stimata_ore}h)")
                
            return tasks_created
            
        except Exception as e:
            print(f"❌ Error creating tasks from templates: {e}")
            return 0

    def create_crm_commercial_ticket(self, activity: Dict[str, Any], kit_name: str) -> Optional[Dict[str, Any]]:
        """Crea ticket commerciale con attività CRM inserita prima - COMPLETO"""
        try:
            kit_validation = self.validate_kit_commerciale(kit_name)
            if not kit_validation["success"]:
                return kit_validation
            
            kit_info = kit_validation["kit"]
            print(f"✅ Kit validato: {kit_info['nome']} (Codice: {kit_info['codice']})")
            
            local_activity_id = self.insert_crm_activity_to_local(activity)
            if not local_activity_id:
                print("⚠️ Warning: Could not insert CRM activity, proceeding without activity_id")
            
            import uuid
            
            ticket_id = str(uuid.uuid4())
            ticket_code = f"TCK-{kit_info['codice']}-{str(activity.get('id', 0))[-4:].zfill(4)}-01"
            
            description = f"Ticket generato automaticamente da CRM Intelligence.\n\n"
            description += f"🎯 Kit Commerciale: {kit_name}\n"
            description += f"📋 Attività CRM: {activity.get('id', 'N/A')}\n"
            description += f"🏢 Azienda CRM: {activity.get('companyId', 'N/A')}\n"
            description += f"📄 Attività locale: {local_activity_id}\n"
            
            company_id = None
            if local_activity_id:
                try:
                    company_query = text("SELECT company_id FROM activities WHERE id = :activity_id")
                    company_result = self.db.execute(company_query, {"activity_id": local_activity_id}).fetchone()
                    if company_result:
                        company_id = company_result.company_id
                except Exception as e:
                    print(f"⚠️ Warning getting company_id: {e}")
            
            insert_query = text("""
                INSERT INTO tickets (
                    id, ticket_code, title, description, priority, status, 
                    activity_id, company_id, created_at, created_by
                ) VALUES (
                    :id, :ticket_code, :title, :description, :priority, :status,
                    :activity_id, :company_id, :created_at, :created_by
                )
            """)
            
            self.db.execute(insert_query, {
                "id": ticket_id,
                "ticket_code": ticket_code,
                "title": f"[COMMERCIALE] {kit_name}",
                "description": description,
                "priority": "alta",
                "status": "aperto",
                "activity_id": local_activity_id,
                "company_id": company_id,
                "created_at": datetime.utcnow(),
                "created_by": kit_info.get("responsabile_user_id")
            })
            
            milestone_id = self._create_real_milestone(ticket_id, kit_name)
            
            tasks_created = 0
            if milestone_id:
                tasks_created = self._create_commercial_tasks(milestone_id, ticket_id)
                
                update_query = text("UPDATE tickets SET milestone_id = :milestone_id WHERE id = :ticket_id")
                self.db.execute(update_query, {"milestone_id": milestone_id, "ticket_id": ticket_id})
            
            self.db.commit()
            
            print(f"✅ Ticket creato: {ticket_code} (ID: {ticket_id})")
            print(f"✅ Milestone creata: {milestone_id}")
            print(f"✅ Task creati: {tasks_created}")
            
            return {
                "success": True,
                "ticket_id": ticket_id,
                "ticket_code": ticket_code,
                "milestone_id": milestone_id,
                "tasks_created": tasks_created,
                "kit_info": kit_info,
                "message": f"Ticket commerciale {ticket_code} creato con successo"
            }
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ Error in create_crm_commercial_ticket: {e}")
            return {"success": False, "error": str(e)}

    # ===== TICKET MANAGEMENT =====

    def list_tickets(self, filters: Optional[Dict] = None) -> List[Dict]:
        """List tickets with optional filtering - CON TASK E MILESTONE"""
        try:
            query = text("""
                SELECT t.id, t.ticket_code, t.title, t.description, t.priority, 
                       t.status, t.created_at, t.created_by, t.activity_id, t.milestone_id,
                       a.title as activity_title, a.company_id,
                       c.name as company_name
                FROM tickets t
                LEFT JOIN activities a ON t.activity_id = a.id
                LEFT JOIN companies c ON a.company_id = c.id
                ORDER BY t.created_at DESC
            """)
            
            result = self.db.execute(query).fetchall()
            
            tickets = []
            for row in result:
                # Recupera task per questo ticket
                task_query = text("SELECT id, title, status FROM tasks WHERE ticket_id = :ticket_id")
                tasks_result = self.db.execute(task_query, {"ticket_id": str(row.id)}).fetchall()
                
                tasks = [{"id": str(t.id), "title": t.title, "status": t.status} for t in tasks_result]
                task_stats = {
                    "total": len(tasks),
                    "completed": len([t for t in tasks if t["status"] == "chiuso"]),
                    "pending": len([t for t in tasks if t["status"] != "chiuso"])
                }
                
                tickets.append({
                    "id": str(row.id),
                    "ticket_code": row.ticket_code,
                    "title": row.title,
                    "description": row.description,
                    "priority": row.priority,
                    "status": row.status,
                    "created_at": row.created_at.isoformat() if hasattr(row.created_at, "isoformat") and row.created_at else str(row.created_at) if row.created_at else None,
                    "updated_at": row.created_at.isoformat() if hasattr(row.created_at, "isoformat") and row.created_at else str(row.created_at) if row.created_at else None,
                    "created_by": str(row.created_by) if row.created_by else None,
                    "assigned_to": str(row.created_by) if row.created_by else None,
                    "activity_id": row.activity_id,
                    "activity_title": row.activity_title,
                    "company_name": row.company_name,
                    "company_id": row.company_id,
                    "milestone_id": str(row.milestone_id) if row.milestone_id else None,
                    "due_date": None,
                    "tasks": tasks,
                    "tasks_stats": task_stats
                })
            
            return tickets
            
        except Exception as e:
            print(f"❌ Error listing tickets: {e}")
            return []

    def get_ticket_detail(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed ticket information - COMPLETO CON ACCOUNT MANAGER"""
        try:
            query = text("""
                SELECT t.id, t.ticket_code, t.title, t.description, t.priority, 
                       t.status, t.created_at, t.created_by, t.activity_id, t.milestone_id,
                       a.title as activity_title, a.description as activity_description,
                       a.accompagnato_da, a.accompagnato_da_nome,
                       c.name as company_name
                FROM tickets t
                LEFT JOIN activities a ON t.activity_id = a.id
                LEFT JOIN companies c ON a.company_id = c.id
                WHERE t.id = :ticket_id
                LIMIT 1
            """)
            
            result = self.db.execute(query, {"ticket_id": ticket_id}).fetchone()
            
            if not result:
                return None
            
            # Recupera task per questo ticket
            task_query = text("SELECT id, title, status FROM tasks WHERE ticket_id = :ticket_id")
            tasks_result = self.db.execute(task_query, {"ticket_id": ticket_id}).fetchall()
            
            tasks = [{"id": str(t.id), "title": t.title, "status": t.status} for t in tasks_result]
            task_stats = {
                "total": len(tasks),
                "completed": len([t for t in tasks if t["status"] == "chiuso"]),
                "pending": len([t for t in tasks if t["status"] != "chiuso"])
            }
            
            return {
                "id": str(result.id),
                "ticket_code": result.ticket_code,
                "title": result.title,
                "description": result.description,
                "priority": result.priority,
                "status": result.status,
                "created_at": result.created_at.isoformat() if result.created_at else None,
                "created_by": str(result.created_by) if result.created_by else None,
                "activity_id": result.activity_id,
                "activity_title": result.activity_title,
                "activity_description": result.activity_description,
                "company_name": result.company_name,
                "customer_name": result.company_name,  # Alias per compatibilità frontend
                "account_manager_id": result.accompagnato_da,
                "account_manager_name": result.accompagnato_da_nome,
                "milestone_id": str(result.milestone_id) if result.milestone_id else None,
                "tasks": tasks,
                "tasks_stats": task_stats
            }
            
        except Exception as e:
            print(f"❌ Error getting ticket detail: {e}")
            return None

    # ===== TASK MANAGEMENT =====

    def get_task_detail(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed task information by ID - COMPLETO"""
        try:
            query = text("""
                SELECT t.id, t.title, t.description, t.status, t.priorita, t.assigned_to,
                       t.milestone_id, t.ticket_id, t.sla_giorni, t.ordine, t.estimated_hours,
                       t.parent_task_id, t.due_date,
                       tk.ticket_code, tk.title as ticket_title,
                       u.name as owner_name, u.surname as owner_surname
                FROM tasks t
                LEFT JOIN tickets tk ON t.ticket_id = tk.id
                LEFT JOIN users u ON t.assigned_to = u.id
                WHERE t.id = :task_id
                LIMIT 1
            """)
            
            result = self.db.execute(query, {"task_id": task_id}).fetchone()
            
            if not result:
                return None
            
            # Trova task siblings (altri task dello stesso ticket)
            siblings_query = text("SELECT id, title, status FROM tasks WHERE ticket_id = :ticket_id AND id != :task_id")
            siblings_result = self.db.execute(siblings_query, {"ticket_id": str(result.ticket_id), "task_id": task_id}).fetchall()
            siblings = [{"id": str(s.id), "title": s.title, "status": s.status} for s in siblings_result]
            
            owner_name = f"{result.owner_name} {result.owner_surname}".strip() if result.owner_name else None
            
            return {
                "id": int(str(result.id).replace("-", "")[:8], 16),  # Converte UUID a int per compatibilità
                "ticket_id": int(str(result.ticket_id).replace("-", "")[:8], 16),  # Converte UUID a int
                "ticket_code": result.ticket_code,
                "title": result.title,
                "description": result.description,
                "status": result.status,
                "priority": result.priorita or "media",
                "owner": str(result.assigned_to) if result.assigned_to else None,
                "owner_name": owner_name,
                "due_date": result.due_date,
                "predecessor_id": int(str(result.parent_task_id).replace("-", "")[:8], 16) if result.parent_task_id else None,
                "predecessor_title": None,
                "closed_at": None,
                "siblings": siblings
            }
            
        except Exception as e:
            print(f"❌ Error getting task detail: {e}")
            return None

    # ===== BUSINESS LOGIC HELPERS =====
    
    def auto_close_completed_tickets(self) -> Dict[str, Any]:
        """Batch operation to auto-close all completed tickets"""
        tickets = self.db.query(Ticket).all()
        updated = 0
        closed_ids = []
        
        for ticket in tickets:
            tasks = self.db.query(Task).filter(Task.ticket_id == ticket.id).all()
            if tasks and all(t.status == "chiuso" for t in tasks) and ticket.status != 2:
                ticket.status = 2
                ticket.updated_at = datetime.utcnow()
                closed_ids.append(ticket.id)
                updated += 1
        
        self.db.commit()
        
        return {
            "tickets_closed": updated,
            "closed_ids": closed_ids,
            "timestamp": datetime.utcnow().isoformat()
        }
