from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.models.er_models import TaskGlobal

router = APIRouter(prefix="/tasks-global", tags=["tasks-global"])

# =====================================
# SCHEMAS
# =====================================

class TaskGlobalCreate(BaseModel):
    tsk_code: str
    tsk_description: Optional[str] = None
    tsk_type: str = 'standard'
    tsk_category: Optional[str] = None
    sla_giorni: Optional[int] = None
    warning_giorni: int = 1
    escalation_giorni: int = 1
    priorita: str = "normale"
    created_at: Optional[datetime] = None

class TaskGlobalUpdate(BaseModel):
    tsk_code: Optional[str] = None
    tsk_description: Optional[str] = None
    tsk_type: Optional[str] = None
    tsk_category: Optional[str] = None
    sla_giorni: Optional[int] = None
    warning_giorni: int = 1
    escalation_giorni: int = 1
    priorita: str = "normale"
    created_at: Optional[datetime] = None

class TaskGlobalResponse(BaseModel):
    id: int
    tsk_code: str
    tsk_description: Optional[str]
    tsk_type: str
    tsk_category: Optional[str]
    sla_giorni: Optional[int] = None
    warning_giorni: int = 1
    escalation_giorni: int = 1
    priorita: str = "normale"
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# =====================================
# ENDPOINTS
# =====================================

@router.get("/", response_model=List[TaskGlobalResponse])
async def list_tasks_global(
    category: Optional[str] = None,
    task_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lista tutti i task globali con filtri opzionali"""
    query = db.query(TaskGlobal)
    
    if category:
        query = query.filter(TaskGlobal.tsk_category == category)
    if task_type:
        query = query.filter(TaskGlobal.tsk_type == task_type)
        
    tasks = query.order_by(TaskGlobal.tsk_category, TaskGlobal.tsk_code).all()
    return tasks

@router.post("/", response_model=TaskGlobalResponse)
async def create_task_global(
    task_data: TaskGlobalCreate,
    db: Session = Depends(get_db)
):
    """Crea un nuovo task globale"""
    
    # Verifica che il codice non esista già
    existing = db.query(TaskGlobal).filter(TaskGlobal.tsk_code == task_data.tsk_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Codice task già esistente")
    
    try:
        db_task = TaskGlobal(
            tsk_code=task_data.tsk_code,
            tsk_description=task_data.tsk_description,
            tsk_type=task_data.tsk_type,
            tsk_category=task_data.tsk_category,
            sla_giorni=task_data.sla_giorni,
            warning_giorni=task_data.warning_giorni,
            escalation_giorni=task_data.escalation_giorni,
            priorita=task_data.priorita
        )
        
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        
        return db_task
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore creazione task: {str(e)}")

@router.put("/{task_id}", response_model=TaskGlobalResponse)
async def update_task_global(
    task_id: int,
    task_data: TaskGlobalUpdate,
    db: Session = Depends(get_db)
):
    """Aggiorna un task globale esistente"""
    
    task = db.query(TaskGlobal).filter(TaskGlobal.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task non trovato")
    
    try:
        update_data = task_data.dict(exclude_unset=True)

        # Gestione speciale per tsk_code (verifica duplicati)
        if "tsk_code" in update_data:
            new_code = update_data["tsk_code"]
            if new_code != task.tsk_code:
                existing = db.query(TaskGlobal).filter(
                    TaskGlobal.tsk_code == new_code,
                    TaskGlobal.id != task_id
                ).first()
                if existing:
                    raise HTTPException(status_code=400, detail="Codice task già esistente")
        for field, value in update_data.items():
            setattr(task, field, value)
        
        db.commit()
        db.refresh(task)
        
        return task
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore aggiornamento task: {str(e)}")

@router.delete("/{task_id}")
async def delete_task_global(
    task_id: int,
    db: Session = Depends(get_db)
):
    """Elimina un task globale"""
    
    task = db.query(TaskGlobal).filter(TaskGlobal.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task non trovato")
    
    try:
        db.delete(task)
        db.commit()
        return {"message": "Task eliminato con successo"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore eliminazione task: {str(e)}")

@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Ottieni tutte le categorie di task disponibili"""
    
    categories = db.query(TaskGlobal.tsk_category).distinct().filter(
        TaskGlobal.tsk_category.isnot(None)
    ).all()
    
    return [cat[0] for cat in categories if cat[0]]
