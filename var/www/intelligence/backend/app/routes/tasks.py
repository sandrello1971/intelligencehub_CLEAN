"""
Intelligence API - Tasks Routes
API endpoints for task management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.modules.ticketing.services import TicketingService
from app.modules.ticketing.schemas import (
    TaskResponse, TaskUpdate, TaskListItem, TaskFilters
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/{task_id}", response_model=TaskResponse)
def get_task_detail(task_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific task"""
    service = TicketingService(db)
    task = service.get_task_detail(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task non trovato")
    
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    """Update a task with business logic"""
    service = TicketingService(db)
    
    # Convert Pydantic model to dict, excluding None values
    update_data = task_update.dict(exclude_unset=True)
    
    updated_task = service.update_task(task_id, update_data)
    
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task non trovato")
    
    return updated_task


@router.get("/", response_model=List[TaskListItem])
def list_tasks(
    ticket_id: Optional[int] = Query(None, description="Filter by ticket ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    owner: Optional[str] = Query(None, description="Filter by owner"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    db: Session = Depends(get_db)
):
    """List tasks with optional filtering"""
    service = TicketingService(db)
    
    # Build filters dict
    filters = {}
    if status:
        filters["status"] = status
    if owner:
        filters["owner"] = owner  
    if priority:
        filters["priority"] = priority
    
    tasks = service.list_tasks(ticket_id=ticket_id, filters=filters)
    return tasks


@router.post("/{task_id}/confirm-create-opportunities")
def confirm_create_opportunities(task_id: int, db: Session = Depends(get_db)):
    """Confirm creation of opportunities from task services"""
    service = TicketingService(db)
    task = service.get_task_detail(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task non trovato")
    
    if not task.get("ticket_id"):
        raise HTTPException(status_code=400, detail="Task non collegato a ticket")
    
    # This would integrate with the opportunities module
    
    return {
        "message": "Opportunities creation confirmed",
        "task_id": task_id,
        "ticket_id": task["ticket_id"]
    }
