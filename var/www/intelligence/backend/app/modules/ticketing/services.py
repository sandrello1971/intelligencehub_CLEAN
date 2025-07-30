"""
Intelligence Ticketing Module - Services
Business logic for ticket and task management
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.models.task import Task
from app.models.ticket import Ticket
from app.models.users import User
from app.models.activity import Activity


class TicketingService:
    """Core service for ticket and task management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ===== TASK MANAGEMENT =====
    
    def get_task_detail(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed task information with relationships - Production Version"""
        from sqlalchemy import text
        
        # Query SQL diretta basata sui dati reali del database
        sql_query = text("""
            SELECT 
                t.id,
                t.title,
                t.description,
                t.status,
                t.priorita,
                t.assigned_to,
                t.due_date,
                t.created_at,
                t.milestone_id,
                t.ticket_id as direct_ticket_id,
                
                -- Milestone info
                m.title as milestone_name,
                m.due_date as milestone_due_date,
                
                -- Ticket through milestone
                tk_milestone.id as ticket_via_milestone_id,
                tk_milestone.ticket_code as ticket_via_milestone_code,
                tk_milestone.title as ticket_via_milestone_title,
                
                -- Ticket direct (if exists)
                tk_direct.id as ticket_direct_id,
                tk_direct.ticket_code as ticket_direct_code,
                tk_direct.title as ticket_direct_title,
                
                -- Owner info
                u.name as owner_first_name,
                u.surname as owner_last_name,
                
                -- Activity info for account manager
                a.owner_name as account_manager
                
            FROM tasks t
            LEFT JOIN milestones m ON t.milestone_id = m.id
            LEFT JOIN tickets tk_milestone ON tk_milestone.milestone_id = t.milestone_id
            LEFT JOIN tickets tk_direct ON tk_direct.id = t.ticket_id
            LEFT JOIN users u ON u.id = t.assigned_to
            LEFT JOIN activities a ON (
                a.id = tk_milestone.activity_id OR 
                a.id = tk_direct.activity_id
            )
            WHERE t.id = :task_id
            LIMIT 1
        """)
        
        try:
            result = self.db.execute(sql_query, {"task_id": str(task_id)}).fetchone()
            
            if not result:
                return None
            
            # Determina quale ticket usare (priorità: diretto -> via milestone)
            ticket_id = None
            ticket_code = None
            ticket_title = None
            
            if result.direct_ticket_id:
                ticket_id = str(result.direct_ticket_id)
                ticket_code = result.ticket_direct_code
                ticket_title = result.ticket_direct_title
            elif result.ticket_via_milestone_id:
                ticket_id = str(result.ticket_via_milestone_id)
                ticket_code = result.ticket_via_milestone_code
                ticket_title = result.ticket_via_milestone_title
            
            # Owner name
            owner_name = None
            if result.owner_first_name and result.owner_last_name:
                owner_name = f"{result.owner_first_name} {result.owner_last_name}"
            
            # Due date priority: task -> milestone
            due_date = result.due_date or result.milestone_due_date
            
            return {
                "id": result.id,
                "title": result.title,
                "description": result.description,
                "status": result.status,
                "priority": result.priorita,  
                "priorita": result.priorita,  # Backward compatibility
                
                # Owner info
                "owner": str(result.assigned_to) if result.assigned_to else None,
                "owner_name": owner_name,
                
                # Milestone info
                "milestone_id": str(result.milestone_id) if result.milestone_id else None,
                "milestone_name": result.milestone_name,
                
                # Ticket info
                "ticket_id": ticket_id,
                "ticket_code": ticket_code,
                "ticket_title": ticket_title,
                
                # Account Manager
                "ticket_account": result.account_manager,
                "account_manager": result.account_manager,
                
                # Dates
                "due_date": due_date,
                "created_at": result.created_at,
                
                # Legacy fields
                "ticket_owner_name": None,
                "predecessor_id": None,
                "predecessor_title": None,
                "closed_at": None,
                "siblings": []
            }
            
        except Exception as e:
            # Log error in production
            print(f"Error in get_task_detail: {e}")
            return None
    def update_task(self, task_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update task with business logic"""
        task = self.db.query(Task).filter(Task.id == str(task_id)).first()
        if not task:
            return None
        
        # Define updatable fields with type casting
        update_fields = {
            "title": str,
            "description": str,
            "status": str,
            "priority": str,
            "owner": str,
            "predecessor_id": int,
            "parent_id": int
        }
        
        # Update fields
        for field, cast_type in update_fields.items():
            if field in update_data:
                value = update_data[field]
                setattr(task, field, cast_type(value) if value is not None else None)
        
        # Handle services if provided
        if "services" in update_data and task.ticket:
            task.ticket.detected_services = update_data["services"]
        
        # Set closed timestamp if status changed to "chiuso"
        if update_data.get("status") == "chiuso" and not task.closed_at:
            task.closed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(task)
        
        # Auto-close ticket if all tasks are closed
        if task.ticket_id:
            self._auto_close_ticket_if_complete(task.ticket_id)
        
        # Sync with CRM if task closed
        if update_data.get("status") == "chiuso" and task.ticket:
            self._sync_task_closure_with_crm(task)
        
        return self.get_task_detail(task_id)
    
    def list_tasks(self, ticket_id: Optional[int] = None, filters: Optional[Dict] = None) -> List[Dict]:
        """List tasks with optional filtering"""
        query = self.db.query(Task)
        
        if ticket_id:
            query = query.filter(Task.ticket_id == ticket_id)
        
        if filters:
            if "status" in filters:
                query = query.filter(Task.status == filters["status"])
            if "owner" in filters:
                query = query.filter(Task.owner == filters["owner"])
            if "priority" in filters:
                query = query.filter(Task.priority == filters["priority"])
        
        tasks = query.all()
        
        return [
            {
                "id": str(t.id),
                "title": t.title,
                "description": t.description,
                "priority": t.priority,
                "status": t.status,
                "due_date": t.due_date,
                "created_at": t.created_at,
                "updated_at": t.updated_at,
                "created_by": str(t.created_by) if t.created_by else None,
                "assigned_to": str(t.assigned_to) if t.assigned_to else None,
                "company_id": t.company_id,
                "milestone_id": str(t.milestone_id) if t.milestone_id else None
            }
            for t in tasks
        ]
    
    # ===== TICKET MANAGEMENT =====
    
    def get_ticket_detail(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed ticket information with tasks"""
        ticket = (
            self.db.query(Ticket)
            .filter(Ticket.id == ticket_id)
            .first()
        )
        
        if not ticket:
            return None
        
        # Get tasks tramite milestone
        tasks = []
        if ticket.milestone_id:
            tasks = (
                self.db.query(Task)
                .filter(Task.milestone_id == ticket.milestone_id)
                .all()
            )
        
        # Enrich tasks with owner information
        enriched_tasks = []
        for task in tasks:
            owner = self.db.query(User).filter(User.id == task.assigned_to).first() if task.assigned_to else None
            owner_name = f"{owner.name} {owner.surname}" if owner else None
            
            enriched_tasks.append({
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "priority": getattr(task, "priorita", "normale"),
                "assigned_to": str(task.assigned_to) if task.assigned_to else None,
                "owner_name": owner_name,
                "due_date": task.due_date,
                "created_at": task.created_at
            })
        
        # Get owner details
        owner_user = None
        if ticket.created_by:
            owner_user = self.db.query(User).filter(User.id == ticket.created_by).first()
        
        # Get company details for customer name
        customer_name = None
        if ticket.company_id:
            from app.models.company import Company
            company = self.db.query(Company).filter(Company.id == ticket.company_id).first()
            customer_name = company.nome if company else None
        
        return {
            "id": str(ticket.id),
            "ticket_code": ticket.ticket_code,
            "title": ticket.title,
            "description": ticket.description,
            "priority": ticket.priority,
            "status": ticket.status,
            "due_date": ticket.due_date,
            "created_at": ticket.created_at,
            "updated_at": ticket.updated_at,
            "created_by": str(ticket.created_by) if ticket.created_by else None,
            "assigned_to": str(ticket.assigned_to) if ticket.assigned_to else None,
            "company_id": ticket.company_id,
            "milestone_id": str(ticket.milestone_id) if ticket.milestone_id else None,
            "workflow_milestone_id": ticket.workflow_milestone_id,
            "activity_id": ticket.activity_id,
            "owner": f"{owner_user.name} {owner_user.surname}" if owner_user else "Non assegnato",
            "customer_name": customer_name or "N/A",
            "tasks": enriched_tasks,
            "tasks_stats": {
                "total": len(enriched_tasks),
                "completed": len([t for t in enriched_tasks if t["status"] in ["completed", "chiuso"]]),
                "pending": len([t for t in enriched_tasks if t["status"] not in ["completed", "chiuso"]])
            }
        }
    
    def list_tickets(self, filters: Optional[Dict] = None) -> List[Dict]:
        """List tickets with optional filtering"""
        query = self.db.query(Ticket)
        
        if filters:
            if "priority" in filters:
                priority_map = {"alta": 2, "media": 1, "bassa": 0}
                priority_value = priority_map.get(filters["priority"].lower())
                if priority_value is not None:
                    query = query.filter(Ticket.priority == priority_value)
            
            if "status" in filters:
                query = query.filter(Ticket.status == filters["status"])
            
            if "customer_name" in filters:
                query = query.filter(Ticket.customer_name.ilike(f"%{filters['customer_name']}%"))
        
        tickets = query.all()
        
        return [
            {
                "id": str(t.id),
                "ticket_code": t.ticket_code,
                "title": t.title,
                "description": t.description,
                "priority": t.priority,
                "status": t.status,
                "due_date": t.due_date,
                "created_at": t.created_at,
                "updated_at": t.updated_at,
                "created_by": str(t.created_by) if t.created_by else None,
                "assigned_to": str(t.assigned_to) if t.assigned_to else None,
                "company_id": t.company_id,
                "milestone_id": str(t.milestone_id) if t.milestone_id else None
            }
            for t in tickets
        ]
    
    # ===== BUSINESS LOGIC HELPERS =====
    
    def _auto_close_ticket_if_complete(self, ticket_id: int) -> bool:
        """Auto-close ticket if all tasks are completed"""
        ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            return False
        
        all_tasks = self.db.query(Task).filter(Task.ticket_id == ticket_id).all()
        
        if all_tasks and all(t.status == "chiuso" for t in all_tasks) and ticket.status != 2:
            ticket.status = 2  # 2 = chiuso
            ticket.updated_at = datetime.utcnow()
            self.db.commit()
            return True
        
        return False
    
    def _sync_task_closure_with_crm(self, task: Task) -> None:
        """Sync task closure with external CRM"""
        # TODO: Implement CRM sync logic
        # This would call the CRM integration module
        pass
    
    def auto_close_completed_tickets(self) -> Dict[str, Any]:
        """Batch operation to auto-close all completed tickets"""
        tickets = self.db.query(Ticket).all()
        updated = 0
        closed_ids = []
        
        for ticket in tickets:
            tasks = self.db.query(Task).filter(Task.ticket_id == ticket.id).all()
            if tasks and all(t.status == "chiuso" for t in tasks) and ticket.status != 2:
                ticket.status = 2  # 2 = chiuso
                ticket.updated_at = datetime.utcnow()
                closed_ids.append(ticket.id)
                updated += 1
        
        self.db.commit()
        
        return {
            "tickets_closed": updated,
            "closed_ids": closed_ids,
            "timestamp": datetime.utcnow().isoformat()
        }

    # ===== COMMERCIAL METHODS =====
    
    def create_commercial_commessa(self, request_data: Dict[str, Any], current_user_id: str) -> Dict[str, Any]:
        """Crea una commessa commerciale da un kit commerciale"""
        try:
            from app.models.kit_commerciali import KitCommerciale, KitArticolo
            from app.models.commesse import Commessa
            from app.models.company import Company
            from app.services.crm.crmsdk import create_crm_activity
            import uuid
            
            # Validazione input
            company_id = request_data.get("company_id")
            kit_id = request_data.get("kit_commerciale_id") 
            notes = request_data.get("notes", "")
            
            # Trova azienda
            company = self.db.query(Company).filter(Company.id == company_id).first()
            if not company:
                return {"success": False, "error": "Azienda non trovata"}
            
            # Trova kit commerciale
            kit = self.db.query(KitCommerciale).filter(
                KitCommerciale.id == kit_id,
                KitCommerciale.attivo == True
            ).first()
            if not kit:
                return {"success": False, "error": "Kit commerciale non trovato"}
            
            # Genera codice commessa univoco
            commessa_code = f"COM-{kit.nome[:3].upper()}-{str(uuid.uuid4())[:8]}"
            
            # Crea la commessa
            nuova_commessa = Commessa(
                codice=commessa_code,
                name=f"{kit.nome} - {company.nome}",
                descrizione=f"Commessa generata da kit '{kit.nome}'\n\nNote: {notes}",
                client_id=company_id,
                created_by=current_user_id,
                status="active"
            )
            
            self.db.add(nuova_commessa)
            self.db.flush()  # Per ottenere l'ID
            
            # Crea attività CRM per tracciamento commerciale
            crm_activity_id = None
            try:
                crm_data = {
                    "subject": f"Commessa {kit.nome} - {company.nome}",
                    "description": f"Commessa commerciale per {kit.nome}\n\nCliente: {company.nome}\nNote: {notes}",
                    "companyId": company_id,
                    "ownerId": current_user_id
                }
                crm_activity_id = create_crm_activity(crm_data)
                print(f"[CRM] Attività creata con ID: {crm_activity_id}")
            except Exception as e:
                print(f"[WARNING] CRM activity creation failed: {e}")
            
            # Trova articoli del kit
            kit_articoli = self.db.query(KitArticolo).filter(
                KitArticolo.kit_commerciale_id == kit_id
            ).all()
            
            servizi_inclusi = []
            for ka in kit_articoli:
                if ka.articolo:
                    servizi_inclusi.append(ka.articolo.nome)
            
            self.db.commit()
            
            return {
                "success": True,
                "commessa_id": str(nuova_commessa.id),
                "commessa_code": commessa_code,
                "kit_info": {"nome": kit.nome, "id": kit.id},
                "company_info": {"nome": company.nome, "id": company.id},
                "servizi_inclusi": servizi_inclusi,
                "crm_activity_id": crm_activity_id,
                "message": f"Commessa {commessa_code} creata con successo"
            }
            
        except Exception as e:
            self.db.rollback()
            return {"success": False, "error": str(e)}
