"""
Intelligence Ticketing Module - Services
Business logic for ticket and task management
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.task import Task
from app.models.ticket import Ticket
from app.models.users import User
from app.models.activity import Activity


class TicketingService:
    """Core service for ticket and task management - VERSIONE COMPLETA"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def validate_kit_commerciale(self, kit_identifier: str) -> Optional[Dict[str, Any]]:
        """Validazione kit commerciale - VERSIONE SQL PURA"""
        try:
            # Query SQL diretta per evitare import problematici
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
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    def insert_crm_activity_to_local(self, crm_activity: Dict[str, Any]) -> Optional[int]:
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
            
            # Trova company_id se presente
            company_id = None
            if crm_activity.get('companyId'):
                try:
                    company_query = text('SELECT id FROM companies WHERE id = :crm_id')
                    company_result = self.db.execute(company_query, {'crm_id': str(crm_activity['companyId'])}).fetchone()
                    if company_result:
                        company_id = company_result.id
                except Exception:
                    pass  # Company non trovata, procedi senza
            
            result = self.db.execute(insert_query, {
                'title': crm_activity.get('subject', 'Attività CRM'),
                'description': crm_activity.get('description', ''),
                'status': 'attiva',
                'priority': 'media', 
                'created_at': datetime.utcnow(),
                'customer_name': crm_activity.get('customerName', ''),
                'company_id': company_id
            }).fetchone()
            
            local_activity_id = result.id if result else None
            print(f'✅ CRM activity {crm_activity["id"]} → local activity {local_activity_id}')
            return local_activity_id
            
        except Exception as e:
            print(f'❌ Error inserting CRM activity: {e}')
            return None

    def create_crm_commercial_ticket(self, activity: Dict[str, Any], kit_name: str) -> Optional[Dict[str, Any]]:
        """Crea ticket commerciale con attività CRM inserita prima"""
        try:
            # 1. Validazione kit
            kit_validation = self.validate_kit_commerciale(kit_name)
            if not kit_validation["success"]:
                return kit_validation
            
            kit_info = kit_validation["kit"]
            print(f"✅ Kit validato: {kit_info['nome']} (Codice: {kit_info['codice']})")
            
            # 2. Inserisci attività CRM nella tabella locale PRIMA del ticket
            local_activity_id = self.insert_crm_activity_to_local(activity)
            if not local_activity_id:
                print("⚠️ Warning: Could not insert CRM activity, proceeding without activity_id")
            
            # 3. Crea ticket con riferimento all'attività locale
            import uuid
            
            ticket_id = str(uuid.uuid4())
            ticket_code = f"TCK-{kit_info['codice']}-{str(activity.get('id', 0))[-4:].zfill(4)}-01"
            
            description = f"Ticket generato automaticamente da CRM Intelligence.\n\n"
            description += f"🎯 Kit Commerciale: {kit_name}\n"
            description += f"📋 Attività CRM: {activity.get('id', 'N/A')}\n"
            description += f"🏢 Azienda CRM: {activity.get('companyId', 'N/A')}\n"
            description += f"📄 Attività locale: {local_activity_id}\n"
            
            # Trova company_id dall'attività appena creata
            company_id = None
            if local_activity_id:
                try:
                    company_query = text("SELECT company_id FROM activities WHERE id = :activity_id")
                    company_result = self.db.execute(company_query, {"activity_id": local_activity_id}).fetchone()
                    if company_result:
                        company_id = company_result.company_id
                except Exception as e:
                    print(f"⚠️ Warning getting company_id: {e}")
            
            # INSERIMENTO SQL con activity_id e company_id
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
                "activity_id": local_activity_id,  # USA ID LOCALE
                "company_id": company_id,  # USA COMPANY_ID DALL'ACTIVITY
                "created_at": datetime.utcnow(),
                "created_by": kit_info.get("responsabile_user_id")
            })
            
            # 4. Crea milestone reale
            milestone_id = self._create_real_milestone(ticket_id, kit_name)
            
            # 5. Crea task del workflow commerciale
            tasks_created = 0
            if milestone_id:
                tasks_created = self._create_commercial_tasks(milestone_id, ticket_id)
                
                # 6. Aggiorna ticket con milestone_id reale
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
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}

    def list_tickets(self, filters: Optional[Dict] = None) -> List[Dict]:
        """List tickets with optional filtering"""
        try:
            query = text("""
                SELECT t.id, t.ticket_code, t.title, t.description, t.priority, 
                       t.status, t.created_at, t.created_by, t.activity_id,
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
                tickets.append({
                    "id": str(row.id),
                    "ticket_code": row.ticket_code,
                    "title": row.title,
                    "description": row.description,
                    "priority": row.priority,
                    "status": row.status,
                    "created_at": row.created_at.isoformat() if hasattr(row.created_at, "isoformat") and row.created_at else str(row.created_at) if row.created_at else None,
                    "updated_at": row.created_at.isoformat() if hasattr(row.created_at, "isoformat") and row.created_at else str(row.created_at) if row.created_at else None,  # Same as created_at for now
                    "created_by": str(row.created_by) if row.created_by else None,
                    "assigned_to": str(row.created_by) if row.created_by else None,  # Same as created_by for now
                    "activity_id": row.activity_id,
                    "activity_title": row.activity_title,
                    "company_name": row.company_name,
                    "company_id": row.company_id,  # Company ID from activity
                    "milestone_id": None,  # TODO: Add proper milestone_id
                    "due_date": None  # No due date for now
                })
            
            return tickets
            
        except Exception as e:
            print(f"❌ Error listing tickets: {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_ticket_detail(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed ticket information"""
        try:
            query = text("""
                SELECT t.id, t.ticket_code, t.title, t.description, t.priority, 
                       t.status, t.created_at, t.created_by, t.activity_id,
                       a.title as activity_title, a.description as activity_description,
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
                "tasks": [],
                "tasks_stats": {"total": 0, "completed": 0, "pending": 0}
            }
            
        except Exception as e:
            print(f"❌ Error getting ticket detail: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _create_real_milestone(self, ticket_id: str, kit_name: str) -> Optional[str]:
        """Crea milestone reale per il ticket commerciale"""
        try:
            import uuid
            milestone_id = str(uuid.uuid4())
            
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
                "workflow_milestone_id": 1,  # Default workflow
                "due_date": None
            })
            
            return milestone_id
            
        except Exception as e:
            print(f"❌ Error creating milestone: {e}")
            return None
    
    def _create_commercial_tasks(self, milestone_id: str, ticket_id: str) -> int:
        """Crea task commerciali standard"""
        tasks_created = 0
        
        commercial_tasks = [
            {"title": "Predisposizione incarico", "descrizione": "Predisporre documentazione incarico", "ordine": 1, "sla_giorni": 2},
            {"title": "Invio incarico", "descrizione": "Inviare incarico al cliente", "ordine": 2, "sla_giorni": 1},
            {"title": "Firma incarico", "descrizione": "Ottenere firma dal cliente", "ordine": 3, "sla_giorni": 7},
            {"title": "Archiviazione documenti", "descrizione": "Archiviare documentazione", "ordine": 4, "sla_giorni": 1}
        ]
        
        try:
            for task_data in commercial_tasks:
                import uuid
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
                    "title": task_data["title"],
                    "description": task_data["descrizione"],
                    "status": "todo",
                    "priorita": "alta",
                    "milestone_id": milestone_id,
                    "ticket_id": ticket_id,
                    "sla_giorni": task_data["sla_giorni"],
                    "ordine": task_data["ordine"]
                })
                
                tasks_created += 1
                
            return tasks_created
            
        except Exception as e:
            print(f"❌ Error creating tasks: {e}")
            return 0
