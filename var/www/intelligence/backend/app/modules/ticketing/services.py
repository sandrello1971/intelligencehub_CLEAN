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
    
    def get_task_detail(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed task information with relationships"""
        task = (
            self.db.query(Task)
            .options(
                joinedload(Task.owner_ref),
                joinedload(Task.predecessor_ref),
                joinedload(Task.ticket).joinedload(Ticket.tasks)
            )
            .filter(Task.id == task_id)
            .first()
        )
        
        if not task:
            return None
        
        # Get owner details
        owner_user = (
            self.db.query(User).filter(User.id == str(task.owner)).first() 
            if task.owner else None
        )
        
        # Get due date from ticket if not set on task
        due_date = task.due_date or (task.ticket.due_date if task.ticket else None)
        
        return {
            "id": task.id,
            "ticket_id": task.ticket_id,
            "ticket_code": task.ticket.ticket_code if task.ticket else None,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "owner": task.owner,
            "owner_name": f"{owner_user.name} {owner_user.surname}" if owner_user else None,
            "due_date": due_date,
            "predecessor_id": task.predecessor_id,
            "predecessor_title": task.predecessor_ref.title if task.predecessor_ref else None,
            "closed_at": task.closed_at,
            "siblings": [
                {"id": t.id, "title": t.title, "status": t.status}
                for t in (task.ticket.tasks if task.ticket else [])
                if t.id != task.id
            ]
        }
    
    def update_task(self, task_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update task with business logic"""
        task = self.db.query(Task).filter(Task.id == task_id).first()
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
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "status": t.status,
                "priority": t.priority,
                "ticket_id": t.ticket_id,
                "owner": t.owner,
                "predecessor_id": t.predecessor_id,
                "milestone_id": t.milestone_id,
                "closed_at": t.closed_at
            }
            for t in tasks
        ]
    
    # ===== TICKET MANAGEMENT =====
    
    def get_ticket_detail(self, ticket_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed ticket information with tasks and activities"""
        ticket = (
            self.db.query(Ticket)
            .options(
                joinedload(Ticket.tasks),
                joinedload(Ticket.activity)
            )
            .filter(Ticket.id == ticket_id)
            .first()
        )
        
        if not ticket:
            return None
        
        # Get account name from activity
        account_name = (
            ticket.activity.owner_name 
            if ticket.activity and ticket.activity.owner_name 
            else None
        )
        
        # Enrich tasks with owner information
        enriched_tasks = []
        for task in (ticket.tasks or []):
            owner = self.db.query(User).filter(User.id == str(task.owner)).first() if task.owner else None
            owner_name = f"{owner.name} {owner.surname}" if owner else None
            
            enriched_tasks.append({
                "id": task.id,
                "title": task.title,
                "status": task.status,
                "priority": task.priority,
                "owner": task.owner,
                "owner_name": owner_name,
                "customer_name": ticket.customer_name,
                "closed_at": task.closed_at
            })
        
        # Get detected services from activity
        detected_services = ticket.activity.detected_services if ticket.activity else []
        
        return {
            "id": ticket.id,
            "ticket_code": ticket.ticket_code,
            "title": ticket.title,
            "description": ticket.description,
            "priority": ticket.priority,
            "status": ticket.status,
            "due_date": ticket.due_date,
            "created_at": ticket.created_at,
            "updated_at": ticket.updated_at,
            "owner_id": ticket.owner_id,
            "gtd_type": ticket.gtd_type,
            "assigned_to": ticket.assigned_to,
            "owner": ticket.owner,
            "account": account_name,
            "milestone_id": ticket.milestone_id,
            "customer_name": ticket.customer_name,
            "gtd_generated": ticket.gtd_generated,
            "detected_services": detected_services,
            "activity": {
                "id": ticket.activity.id if ticket.activity else None,
                "description": ticket.activity.description if ticket.activity else None,
                "detected_services": detected_services
            },
            "tasks": enriched_tasks,
            "tasks_stats": {
                "total": len(enriched_tasks),
                "completed": len([t for t in enriched_tasks if t["status"] == "chiuso"]),
                "pending": len([t for t in enriched_tasks if t["status"] != "chiuso"])
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
                "id": t.id,
                "ticket_code": t.ticket_code,
                "title": t.title,
                "description": t.description,
                "priority": t.priority,
                "status": t.status,
                "due_date": t.due_date,
                "created_at": t.created_at,
                "updated_at": t.updated_at,
                "owner_id": t.owner_id,
                "gtd_type": t.gtd_type,
                "assigned_to": t.assigned_to,
                "owner": t.owner,
                "milestone_id": t.milestone_id,
                "customer_name": t.customer_name,
                "gtd_generated": t.gtd_generated,
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
