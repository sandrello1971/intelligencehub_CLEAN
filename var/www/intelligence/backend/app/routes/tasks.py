"""
Intelligence API - Tasks Routes with SLA Support
API endpoints for task management with 3-level SLA system
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.models.task import Task
from app.models.users import User
from app.schemas.task import (
    TaskCreate, TaskUpdate, TaskResponse, TaskListItem, 
    TaskSLAMonitoring
)

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse)
def create_task(task_data: TaskCreate, db: Session = Depends(get_db)):
    """
    Crea un nuovo task con SLA configurabili
    """
    try:
        # Crea il task
        db_task = Task(
            title=task_data.title,
            description=task_data.description,
            ticket_id=task_data.ticket_id,
            milestone_id=task_data.milestone_id,
            assigned_to=task_data.assigned_to,
            due_date=task_data.due_date,
            
            # SLA configurabili
            sla_giorni=task_data.sla_giorni,
            warning_giorni=task_data.warning_giorni,
            escalation_giorni=task_data.escalation_giorni,
            
            # SLA manuali (se specificati)
            sla_deadline=task_data.sla_deadline,
            warning_deadline=task_data.warning_deadline,
            escalation_deadline=task_data.escalation_deadline,
            
            # Altri campi
            priorita=task_data.priorita,
            estimated_hours=task_data.estimated_hours,
            checklist=task_data.checklist,
            task_metadata=task_data.task_metadata
        )
        
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        
        return db_task
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore creazione task: {str(e)}")

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, db: Session = Depends(get_db)):
    """
    Ottieni dettagli task con ticket collegato - PRODUZIONE
    """
    from sqlalchemy import text
    
    # Query SQL produzione che funziona
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
            t.sla_giorni,
            t.warning_giorni,
            t.escalation_giorni,
            t.sla_deadline,
            t.warning_deadline,
            t.escalation_deadline,
            t.estimated_hours,
            t.actual_hours,
            t.checklist,
            t.task_metadata,
            t.parent_task_id,
            t.company_id,
            t.commessa_id,
            
            -- Milestone info
            m.title as milestone_name,
            
            -- Ticket through milestone
            tk_milestone.id as ticket_via_milestone_id,
            tk_milestone.ticket_code as ticket_via_milestone_code,
            
            -- Ticket direct
            tk_direct.id as ticket_direct_id,
            tk_direct.ticket_code as ticket_direct_code
            
        FROM tasks t
        LEFT JOIN milestones m ON t.milestone_id = m.id
        LEFT JOIN tickets tk_milestone ON tk_milestone.milestone_id = t.milestone_id
        LEFT JOIN tickets tk_direct ON tk_direct.id = t.ticket_id
        WHERE t.id = :task_id
    """)
    
    result = db.execute(sql_query, {"task_id": task_id}).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Task non trovato")
    
    # Determina ticket_id (priorità: diretto -> via milestone)
    final_ticket_id = None
    final_ticket_code = None
    
    if result.direct_ticket_id:
        final_ticket_id = result.direct_ticket_id
        final_ticket_code = result.ticket_direct_code
    elif result.ticket_via_milestone_id:
        final_ticket_id = result.ticket_via_milestone_id  
        final_ticket_code = result.ticket_via_milestone_code
    
    # Costruisci oggetto Task con i campi corretti
    task_data = {
        "id": result.id,
        "title": result.title,
        "description": result.description,
        "status": result.status,
        "priorita": result.priorita,
        "assigned_to": result.assigned_to,
        "due_date": result.due_date,
        "created_at": result.created_at,
        "milestone_id": result.milestone_id,
        "ticket_id": final_ticket_id,
        "ticket_code": final_ticket_code,  # QUESTO È IL FIX PRINCIPALE
        "sla_giorni": result.sla_giorni,
        "warning_giorni": result.warning_giorni,
        "escalation_giorni": result.escalation_giorni,
        "sla_deadline": result.sla_deadline,
        "warning_deadline": result.warning_deadline,
        "escalation_deadline": result.escalation_deadline,
        "estimated_hours": result.estimated_hours,
        "actual_hours": result.actual_hours,
        "checklist": result.checklist,
        "task_metadata": result.task_metadata,
        "parent_task_id": result.parent_task_id,
        "company_id": result.company_id,
        "commessa_id": result.commessa_id
    }
    
    # Crea oggetto Task dal dict
    from app.models.task import Task
    task = Task(**{k: v for k, v in task_data.items() if v is not None})
    
    return task
@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(task_id: str, task_data: TaskUpdate, db: Session = Depends(get_db)):
    """
    Aggiorna task con possibilità di modificare SLA
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task non trovato")
    
    try:
        # Aggiorna campi forniti
        update_data = task_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(task, field, value)
        
        db.commit()
        db.refresh(task)
        
        return task
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore aggiornamento task: {str(e)}")

@router.get("/", response_model=List[TaskListItem])
def list_tasks(
    status: Optional[str] = Query(None, description="Filtra per status"),
    assigned_to: Optional[str] = Query(None, description="Filtra per assegnatario"),
    sla_status: Optional[str] = Query(None, pattern="^(GREEN|YELLOW|ORANGE|RED)$", description="Filtra per stato SLA"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista tasks con filtri SLA
    """
    query = db.query(Task)
    
    # Filtri base
    if status:
        query = query.filter(Task.status == status)
    if assigned_to:
        query = query.filter(Task.assigned_to == assigned_to)
    
    # Filtri SLA
    now = datetime.utcnow()
    if sla_status == "GREEN":
        query = query.filter(Task.warning_deadline > now)
    elif sla_status == "YELLOW":
        query = query.filter(
            and_(Task.warning_deadline <= now, Task.sla_deadline >= now)
        )
    elif sla_status == "ORANGE":
        query = query.filter(
            and_(Task.sla_deadline < now, Task.escalation_deadline >= now)
        )
    elif sla_status == "RED":
        query = query.filter(Task.escalation_deadline < now)
    
    tasks = query.offset(skip).limit(limit).all()
    
    # Aggiungi sla_status calcolato per ogni task
    result = []
    for task in tasks:
        task_dict = {
            "id": task.id,
            "title": task.title,
            "status": task.status,
            "assigned_to": task.assigned_to,
            "sla_deadline": task.sla_deadline,
            "priorita": task.priorita,
            "created_at": task.created_at,
            "sla_status": _calculate_sla_status(task, now),
            "description": task.description,
            "sla_giorni": task.sla_giorni,
            "warning_giorni": task.warning_giorni,
            "escalation_giorni": task.escalation_giorni,
            "warning_deadline": task.warning_deadline,
            "escalation_deadline": task.escalation_deadline,
        }
        result.append(TaskListItem(**task_dict))
    
    return result

@router.get("/sla/monitoring", response_model=TaskSLAMonitoring)
def get_sla_monitoring(db: Session = Depends(get_db)):
    """
    Dashboard monitoring SLA - conta tasks per stato
    """
    now = datetime.utcnow()
    
    # Query per conteggi
    green_count = db.query(Task).filter(Task.warning_deadline > now).count()
    yellow_count = db.query(Task).filter(
        and_(Task.warning_deadline <= now, Task.sla_deadline >= now)
    ).count()
    orange_count = db.query(Task).filter(
        and_(Task.sla_deadline < now, Task.escalation_deadline >= now)
    ).count()
    red_count = db.query(Task).filter(Task.escalation_deadline < now).count()
    
    # Liste dettagliate (prime 10 per categoria)
    green_tasks = db.query(Task).filter(Task.warning_deadline > now).limit(10).all()
    yellow_tasks = db.query(Task).filter(
        and_(Task.warning_deadline <= now, Task.sla_deadline >= now)
    ).limit(10).all()
    orange_tasks = db.query(Task).filter(
        and_(Task.sla_deadline < now, Task.escalation_deadline >= now)
    ).limit(10).all()
    red_tasks = db.query(Task).filter(Task.escalation_deadline < now).limit(10).all()
    
    return TaskSLAMonitoring(
        green_tasks=green_count,
        yellow_tasks=yellow_count,
        orange_tasks=orange_count,
        red_tasks=red_count,
        green_list=[_task_to_list_item(t, now) for t in green_tasks],
        yellow_list=[_task_to_list_item(t, now) for t in yellow_tasks],
        orange_list=[_task_to_list_item(t, now) for t in orange_tasks],
        red_list=[_task_to_list_item(t, now) for t in red_tasks]
    )

@router.delete("/{task_id}")
def delete_task(task_id: str, db: Session = Depends(get_db)):
    """
    Elimina task
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task non trovato")
    
    try:
        db.delete(task)
        db.commit()
        return {"message": "Task eliminato con successo"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore eliminazione task: {str(e)}")

# Helper functions
def _calculate_sla_status(task: Task, now: datetime) -> str:
    """Calcola stato SLA per un task"""
    if not task.sla_deadline:
        return "NO_SLA"
    
    if now < task.warning_deadline:
        return "GREEN"
    elif now <= task.sla_deadline:
        return "YELLOW"
    elif now <= task.escalation_deadline:
        return "ORANGE"
    else:
        return "RED"

def _task_to_list_item(task: Task, now: datetime) -> TaskListItem:
    """Converte Task in TaskListItem"""
    return TaskListItem(
        id=task.id,
        title=task.title,
        status=task.status,
        assigned_to=task.assigned_to,
        sla_deadline=task.sla_deadline,
        sla_status=_calculate_sla_status(task, now),
        priorita=task.priorita,
        description=task.description,
        sla_giorni=task.sla_giorni,
        warning_giorni=task.warning_giorni,
        escalation_giorni=task.escalation_giorni,
        warning_deadline=task.warning_deadline,
        escalation_deadline=task.escalation_deadline,
        created_at=task.created_at
    )
