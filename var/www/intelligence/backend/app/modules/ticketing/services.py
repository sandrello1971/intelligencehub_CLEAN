
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
    
    # ===== UTILITY METHODS =====
    
    def _get_default_workflow_id(self) -> int:
        """Recupera ID del workflow commerciale standard"""
        try:
            query = text("SELECT id FROM workflow_templates WHERE nome = 'Commerciale Standard' LIMIT 1")
            result = self.db.execute(query).fetchone()
            return result.id if result else 1
        except Exception as e:
            print(f"⚠️  Warning getting workflow ID: {e}")
            return 1
    
    def _get_default_milestone_id(self) -> str:
        """Recupera milestone ID di default per task commerciali"""
        try:
            query = text("SELECT id FROM workflow_milestones WHERE workflow_id = :workflow_id LIMIT 1")
            result = self.db.execute(query, {"workflow_id": self._get_default_workflow_id()}).fetchone()
            return str(result.id) if result else "1"
        except Exception as e:
            print(f"⚠️  Warning getting milestone ID: {e}")
            return "1"
    
    def validate_kit_commerciale(self, kit_name: str) -> Dict[str, Any]:
        """Valida l'esistenza di un kit commerciale"""
        try:
            query = text("""
                SELECT k.id, k.nome, k.attivo, a.codice, a.responsabile_user_id
                FROM kit_commerciali k
                LEFT JOIN articoli a ON k.articolo_principale_id = a.id
                WHERE k.nome = :kit_name AND k.attivo = true
                LIMIT 1
            """)
            
            result = self.db.execute(query, {"kit_name": kit_name}).fetchone()
            
            if not result:
                return {
                    "success": False,
                    "error": f"Kit commerciale '{kit_name}' non trovato o non attivo"
                }
            
            return {
                "success": True,
                "kit": {
                    "id": result.id,
                    "nome": result.nome,
                    "codice": result.codice,
                    "attivo": result.attivo,
                    "responsabile_user_id": result.responsabile_user_id
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Errore validazione kit: {str(e)}"
            }
    
    def insert_crm_activity_to_local(self, activity: Dict[str, Any]) -> Optional[int]:
        """Inserisce attività CRM nella tabella activities locale"""
        try:
            insert_query = text("""
                INSERT INTO activities (
                    title, description, status, priority, created_at,
                    customer_name, company_id, owner_id, owner_name,
                    accompagnato_da, accompagnato_da_nome
                ) VALUES (
                    :title, :description, :status, :priority, :created_at,
                    :customer_name, :company_id, :owner_id, :owner_name,
                    :accompagnato_da, :accompagnato_da_nome
                ) RETURNING id
            """)
            
            company_id = activity.get("companyId")  # ID CRM diretto
            if company_id:
                # Verifica che la company esista
                company_query = text("SELECT id FROM companies WHERE id = :company_id LIMIT 1")
                company_result = self.db.execute(company_query, {"company_id": company_id}).fetchone()
                company_id = company_result.id if company_result else None
                company_id = company_result.id if company_result else None
            
            result = self.db.execute(insert_query, {
                "title": activity.get("subject", "Attività CRM"),
                "description": activity.get("description", ""),
                "status": "attiva",
                "priority": "media", 
                "created_at": datetime.utcnow(),
                "customer_name": activity.get("customerName", ""),
                "company_id": company_id,
                "owner_id": activity.get("ownerId"),
                "owner_name": activity.get("ownerName", ""),
                "accompagnato_da": activity.get("accompagnato_da"),
                "accompagnato_da_nome": activity.get("accompagnato_da_nome")
            }).fetchone()
            
            local_activity_id = result.id if result else None
            print(f"✅ Attività CRM inserita localmente: ID {local_activity_id}")
            return local_activity_id
            
        except Exception as e:
            print(f"❌ Error inserting CRM activity: {e}")
            return None
    
    # ===== MILESTONE METHODS =====
    
    def _create_real_milestone(self, ticket_id: str, kit_name: str) -> Optional[str]:
        """Crea milestone reale nel database"""
        try:
            import uuid
            milestone_id = str(uuid.uuid4())
            
            insert_query = text("""
                INSERT INTO milestones (
                    id, title, descrizione, stato
                ) VALUES (
                    :id, :title, :descrizione, :stato
                )
            """)
            
            self.db.execute(insert_query, {
                "id": milestone_id,
                "title": f"Milestone per {kit_name}",
                "descrizione": f"Milestone automatica per kit commerciale {kit_name}",
                "stato": "pianificata"
            })
            
            return milestone_id
            
        except Exception as e:
            print(f"❌ Error creating milestone: {e}")
            return None
    
    def _create_commercial_tasks(self, milestone_id: str, ticket_id: str) -> int:
        """Crea task commerciali dal database - CON ASSIGNED_TO"""
        tasks_created = 0
        
        try:
            # Ottieni il created_by del ticket per assegnare i task
            ticket_query = text("SELECT created_by FROM tickets WHERE id = :ticket_id")
            ticket_result = self.db.execute(ticket_query, {"ticket_id": ticket_id}).fetchone()
            ticket_owner = ticket_result.created_by if ticket_result else None
            
            if not ticket_owner:
                print(f"⚠️ Warning: No ticket owner found for {ticket_id}")
            
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
                        milestone_id, ticket_id, sla_giorni, ordine, estimated_hours, assigned_to
                    ) VALUES (
                        :id, :title, :description, :status, :priorita,
                        :milestone_id, :ticket_id, :sla_giorni, :ordine, :estimated_hours, :assigned_to
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
                    "estimated_hours": task_template.durata_stimata_ore,
                    "assigned_to": ticket_owner
                })
                
                tasks_created += 1
                print(f"   ✅ Created task: {task_template.nome} ({task_template.durata_stimata_ore}h) → Assigned to: {ticket_owner[:8] if ticket_owner else None}")
                
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
            
            # Chiama il hook se lo status è cambiato
            if "status" in update_data and old_status is not None:
                new_status = update_data["status"]
                if old_status != new_status:
                    try:
                        import sys; sys.path.append("/var/www/intelligence/backend"); from app.services.task_status_hooks import on_task_status_changed
                        on_task_status_changed(self.db, task_id, old_status, new_status)
                    except Exception as hook_error:
                        print(f"⚠️ Errore hook task status: {hook_error}")
            
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
                       t.status, t.created_at, t.created_by, t.activity_id, t.milestone_id, t.note,
                       a.title as activity_title, a.company_id,
                       c.name as company_name
                FROM tickets t
                LEFT JOIN activities a ON t.activity_id = a.id
                LEFT JOIN companies c ON t.company_id = c.id
                ORDER BY t.created_at DESC
            """)
            
            result = self.db.execute(query).fetchall()
            
            tickets = []
            for row in result:
                # Recupera task per questo ticket
                task_query = text("SELECT id, title, status FROM tasks WHERE ticket_id = :ticket_id ORDER BY ordine ASC, created_at ASC")
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
                    "note": row.note,
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
                       t.status, t.created_at, t.created_by, t.activity_id, t.milestone_id, t.note,
                       a.title as activity_title, a.description as activity_description,
                       a.accompagnato_da, a.accompagnato_da_nome,
                       c.name as company_name,
                       resp.name as responsabile_name, resp.surname as responsabile_surname,
                       ar.responsabile_user_id,
                       ar.nome as articolo_nome
                FROM tickets t
                LEFT JOIN activities a ON t.activity_id = a.id
                LEFT JOIN companies c ON t.company_id = c.id
                LEFT JOIN articoli ar ON SUBSTRING(t.ticket_code FROM 5 FOR 3) = ar.codice
                LEFT JOIN users resp ON ar.responsabile_user_id = resp.id
                WHERE t.id = :ticket_id
                LIMIT 1
            """)
            
            result = self.db.execute(query, {"ticket_id": ticket_id}).fetchone()
            
            if not result:
                return None
            
            # Recupera task per questo ticket
            task_query = text("SELECT id, title, status FROM tasks WHERE ticket_id = :ticket_id ORDER BY ordine ASC, created_at ASC")
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
                "note": result.note,
                "responsabile_name": f"{result.responsabile_name} {result.responsabile_surname}".strip() if result.responsabile_name else None,
                "responsabile_id": str(result.responsabile_user_id) if result.responsabile_user_id else None,
                "articolo_nome": result.articolo_nome,
                # Campi owner per compatibilità frontend
                "owner": f"{result.responsabile_name} {result.responsabile_surname}".strip() if result.responsabile_name else "Non assegnato",
                "assigned_to": str(result.responsabile_user_id) if result.responsabile_user_id else None,
                "assigned_user_name": f"{result.responsabile_name} {result.responsabile_surname}".strip() if result.responsabile_name else None,
                "tasks": tasks,
                "tasks_stats": task_stats
            }
            
        except Exception as e:
            print(f"❌ Error getting ticket detail: {e}")
            return None

    def update_ticket(self, ticket_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a ticket with new data"""
        try:
            # Costruiamo la query di update dinamicamente
            update_fields = []
            params = {"ticket_id": ticket_id}
            
            # Mappiamo i campi che possono essere aggiornati
            field_mapping = {
                "title": "title",
                "description": "description", 
                "priority": "priority",
                "status": "status",
                "note": "note"
            }
            
            # Solo i campi forniti vengono aggiornati
            for field, db_field in field_mapping.items():
                if field in update_data and update_data[field] is not None:
                    update_fields.append(f"{db_field} = :{field}")
                    params[field] = update_data[field]
            
            if not update_fields:
                return self.get_ticket_detail(ticket_id)
            
            # Eseguiamo l'update
            update_query = text(f"""
                UPDATE tickets 
                SET {", ".join(update_fields)}
                WHERE id = :ticket_id
            """)
            
            self.db.execute(update_query, params)
            self.db.commit()
            
            # Chiama il hook se lo status è cambiato
            if "status" in update_data and old_status is not None:
                new_status = update_data["status"]
                if old_status != new_status:
                    try:
                        import sys; sys.path.append("/var/www/intelligence/backend"); from app.services.task_status_hooks import on_task_status_changed
                        on_task_status_changed(self.db, task_id, old_status, new_status)
                    except Exception as hook_error:
                        print(f"⚠️ Errore hook task status: {hook_error}")
            
            # Restituiamo il ticket aggiornato
            return self.get_ticket_detail(ticket_id)
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ Error updating ticket: {e}")
            return None

    # ===== TASK MANAGEMENT =====

    def list_tasks(self, ticket_id: Optional[int] = None, filters: Optional[Dict] = None) -> List[Dict]:
        """List tasks with optional filtering"""
        try:
            query = text("""
                SELECT t.id, t.title, t.description, t.status, t.priorita as priority,
                       t.assigned_to, t.ticket_id, t.milestone_id, t.due_date, t.note,
                       tk.ticket_code
                FROM tasks t
                LEFT JOIN tickets tk ON t.ticket_id = tk.id
                ORDER BY t.created_at DESC
            """)
            
            result = self.db.execute(query).fetchall()
            
            tasks = []
            for row in result:
                tasks.append({
                    "id": str(row.id),
                    "ticket_id": str(row.ticket_id) if row.ticket_id else None,
                    "title": row.title,
                    "description": row.description,
                    "status": row.status,
                    "priority": row.priority or "media",
                    "owner": str(row.assigned_to) if row.assigned_to else None,
                    "due_date": row.due_date.isoformat() if row.due_date else None,
                    "milestone_id": None,
                    "note": row.note,
                    "predecessor_id": None,
                    "closed_at": None,
                    "responsabile_name": None,
                    "responsabile_id": None,
                    "articolo_nome": None
                })
            
            return tasks
            
        except Exception as e:
            print(f"❌ Error listing tasks: {e}")
            return []

    def get_task_detail(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed task information by ID - COMPLETO"""
        try:
            # Prima prova con task_id diretto (UUID)
            query = text("""
                SELECT t.id, t.title, t.description, t.status, t.priorita, t.assigned_to, t.note,
                       t.milestone_id, t.ticket_id, t.sla_giorni, t.ordine, t.estimated_hours,
                       t.parent_task_id, t.due_date,
                       tk.ticket_code, tk.title as ticket_title,
                       u.name as owner_name, u.surname as owner_surname,
                       resp.name as responsabile_name, resp.surname as responsabile_surname,
                       ar.nome as articolo_nome, ar.responsabile_user_id
                FROM tasks t
                LEFT JOIN tickets tk ON t.ticket_id = tk.id
                LEFT JOIN users u ON t.assigned_to = u.id
                LEFT JOIN activities a ON tk.activity_id = a.id
                LEFT JOIN articoli ar ON SUBSTRING(tk.ticket_code FROM 5 FOR 3) = ar.codice
                LEFT JOIN users resp ON ar.responsabile_user_id = resp.id
                WHERE t.id = :task_id
                LIMIT 1
            """)
            
            result = self.db.execute(query, {"task_id": task_id}).fetchone()
            
            # Se non trova con UUID diretto, prova a cercare per INT convertito
            if not result and task_id.isdigit():
                query_by_int = text("""
                    SELECT t.id, t.title, t.description, t.status, t.priorita, t.assigned_to, t.note,
                           t.milestone_id, t.ticket_id, t.sla_giorni, t.ordine, t.estimated_hours,
                           t.parent_task_id, t.due_date,
                           tk.ticket_code, tk.title as ticket_title,
                           u.name as owner_name, u.surname as owner_surname,
                           resp.name as responsabile_name, resp.surname as responsabile_surname,
                           ar.nome as articolo_nome, ar.responsabile_user_id
                    FROM tasks t
                    LEFT JOIN tickets tk ON t.ticket_id = tk.id
                    LEFT JOIN users u ON t.assigned_to = u.id
                    LEFT JOIN activities a ON tk.activity_id = a.id
                    LEFT JOIN articoli ar ON SUBSTRING(tk.ticket_code FROM 5 FOR 3) = ar.codice
                    LEFT JOIN users resp ON ar.responsabile_user_id = resp.id
                    WHERE (CAST('x' || LPAD(SUBSTR(REPLACE(t.id::text, '-', ''), 1, 8), 8, '0') AS BIT(32))::INT) = :task_id_int
                    LIMIT 1
                """)
                result = self.db.execute(query_by_int, {"task_id_int": int(task_id)}).fetchone()
            
            if not result:
                return None
            
            # Trova task siblings (altri task dello stesso ticket)
            siblings_query = text("SELECT id, title, status FROM tasks WHERE ticket_id = :ticket_id AND id != :task_id")
            siblings_result = self.db.execute(siblings_query, {"ticket_id": str(result.ticket_id), "task_id": task_id}).fetchall()
            siblings = [{"id": str(s.id), "title": s.title, "status": s.status} for s in siblings_result]
            
            owner_name = f"{result.owner_name} {result.owner_surname}".strip() if result.owner_name else None
            
            return {
                "id": str(result.id),
                "ticket_id": str(result.ticket_id),
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
                "note": result.note,
                "responsabile_name": f"{result.responsabile_name} {result.responsabile_surname}".strip() if result.responsabile_name else None,
                "responsabile_id": str(result.responsabile_user_id) if result.responsabile_user_id else None,
                "articolo_nome": result.articolo_nome,
                # Campi owner per compatibilità frontend
                "owner": f"{result.responsabile_name} {result.responsabile_surname}".strip() if result.responsabile_name else "Non assegnato",
                "assigned_to": str(result.responsabile_user_id) if result.responsabile_user_id else None,
                "assigned_user_name": f"{result.responsabile_name} {result.responsabile_surname}".strip() if result.responsabile_name else None,
                "siblings": siblings
            }
            
        except Exception as e:
            print(f"❌ Error getting task detail: {e}")
            return None

    def update_task(self, task_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a task with new data"""
        try:
            # Costruiamo la query di update dinamicamente
            update_fields = []
            params = {"task_id": task_id}
            
            # Mappiamo i campi che possono essere aggiornati
            field_mapping = {
                "title": "title",
                "description": "description",
                "status": "status", 
                "priorita": "priorita",
                "note": "note",
                "assigned_to": "assigned_to"
            }
            
            # Se stiamo aggiornando lo status, recuperiamo quello precedente per il hook
            old_status = None
            if "status" in update_data:
                old_status_query = text("SELECT status FROM tasks WHERE id = :task_id")
                old_status_result = self.db.execute(old_status_query, {"task_id": task_id}).fetchone()
                if old_status_result:
                    old_status = old_status_result[0]

            # Solo i campi forniti vengono aggiornati
            for field, db_field in field_mapping.items():
                if field in update_data and update_data[field] is not None:
                    update_fields.append(f"{db_field} = :{field}")
                    params[field] = update_data[field]
            
            if not update_fields:
                return self.get_task_detail(task_id)
            
            # Eseguiamo l'update
            update_query = text(f"""
                UPDATE tasks 
                SET {", ".join(update_fields)}
                WHERE id = :task_id
            """)
            
            self.db.execute(update_query, params)
            self.db.commit()
            
            # Chiama il hook se lo status è cambiato
            if "status" in update_data and old_status is not None:
                new_status = update_data["status"]
                if old_status != new_status:
                    try:
                        import sys; sys.path.append("/var/www/intelligence/backend"); from app.services.task_status_hooks import on_task_status_changed
                        on_task_status_changed(self.db, task_id, old_status, new_status)
                    except Exception as hook_error:
                        print(f"⚠️ Errore hook task status: {hook_error}")
            
            # Restituiamo il task aggiornato
            return self.get_task_detail(task_id)
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ Error updating task: {e}")
            return None
