from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.routes.auth import get_current_user_dep
from app.schemas.templates import (
    ModelloTaskCreate, ModelloTaskUpdate, ModelloTaskResponse,
    ModelloTicketCreate, ModelloTicketUpdate, ModelloTicketResponse,
    TemplateListItem
)
from app.models.commesse import ModelloTask, ModelloTicket, Milestone
from app.models.users import User

router = APIRouter(prefix="/api/v1/templates", tags=["Template Management"])

# ==============================================
# TASK TEMPLATES
# ==============================================

@router.post("/task-templates", response_model=ModelloTaskResponse)
async def create_task_template(
    template_data: ModelloTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """
    Crea un nuovo modello di task
    """
    try:
        db_template = ModelloTask(
            nome=template_data.nome,
            descrizione=template_data.descrizione,
            categoria=template_data.categoria,
            sla_hours=template_data.sla_hours or 24,
            priorita=template_data.priorita or "medium",
            assignee_default_role=template_data.assignee_default_role,
            checklist=template_data.checklist or [],
            template_content=template_data.template_content,
            tags=template_data.tags or [],
            created_by=current_user.id
        )
        
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        
        return ModelloTaskResponse.from_orm(db_template)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore creazione template task: {str(e)}")

@router.get("/task-templates", response_model=List[ModelloTaskResponse])
async def list_task_templates(
    categoria: Optional[str] = Query(None),
    is_active: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """
    Lista modelli task con filtri
    """
    try:
        query = db.query(ModelloTask).filter(ModelloTask.is_active == is_active)
        
        if categoria:
            query = query.filter(ModelloTask.categoria == categoria)
        
        templates = query.offset(skip).limit(limit).all()
        
        return [ModelloTaskResponse.from_orm(t) for t in templates]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore recupero template task: {str(e)}")

@router.get("/task-templates/{template_id}", response_model=ModelloTaskResponse)
async def get_task_template(
    template_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """
    Dettaglio modello task
    """
    try:
        template = db.query(ModelloTask).filter(ModelloTask.id == template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="Template task non trovato")
        
        return ModelloTaskResponse.from_orm(template)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore recupero template task: {str(e)}")

@router.patch("/task-templates/{template_id}", response_model=ModelloTaskResponse)
async def update_task_template(
    template_id: UUID,
    template_update: ModelloTaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """
    Aggiorna un modello task
    """
    try:
        template = db.query(ModelloTask).filter(ModelloTask.id == template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="Template task non trovato")
        
        # Aggiorna campi forniti
        for field, value in template_update.dict(exclude_unset=True).items():
            setattr(template, field, value)
        
        db.commit()
        db.refresh(template)
        
        return ModelloTaskResponse.from_orm(template)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore aggiornamento template task: {str(e)}")

@router.delete("/task-templates/{template_id}")
async def delete_task_template(
    template_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """
    Disattiva un modello task
    """
    try:
        template = db.query(ModelloTask).filter(ModelloTask.id == template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="Template task non trovato")
        
        template.is_active = False
        db.commit()
        
        return {"message": "Template task disattivato con successo"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore disattivazione template task: {str(e)}")

# ==============================================
# TICKET TEMPLATES
# ==============================================

@router.post("/ticket-templates", response_model=ModelloTicketResponse)
async def create_ticket_template(
    template_data: ModelloTicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """
    Crea un nuovo modello di ticket
    """
    try:
        # Verifica che la milestone esista se specificata
        if template_data.milestone_id:
            milestone = db.query(Milestone).filter(Milestone.id == template_data.milestone_id).first()
            if not milestone:
                raise HTTPException(status_code=404, detail="Milestone non trovata")
        
        db_template = ModelloTicket(
            nome=template_data.nome,
            descrizione=template_data.descrizione,
            milestone_id=template_data.milestone_id,
            task_templates=template_data.task_templates or [],
            auto_assign_rules=template_data.auto_assign_rules or {}
        )
        
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        
        return ModelloTicketResponse.from_orm(db_template)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore creazione template ticket: {str(e)}")

@router.get("/ticket-templates", response_model=List[ModelloTicketResponse])
async def list_ticket_templates(
    milestone_id: Optional[UUID] = Query(None),
    is_active: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """
    Lista modelli ticket con filtri
    """
    try:
        query = db.query(ModelloTicket).filter(ModelloTicket.is_active == is_active)
        
        if milestone_id:
            query = query.filter(ModelloTicket.milestone_id == milestone_id)
        
        templates = query.offset(skip).limit(limit).all()
        
        return [ModelloTicketResponse.from_orm(t) for t in templates]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore recupero template ticket: {str(e)}")

@router.patch("/ticket-templates/{template_id}", response_model=ModelloTicketResponse)
async def update_ticket_template(
    template_id: UUID,
    template_update: ModelloTicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """
    Aggiorna un modello ticket
    """
    try:
        template = db.query(ModelloTicket).filter(ModelloTicket.id == template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="Template ticket non trovato")
        
        # Aggiorna campi forniti
        for field, value in template_update.dict(exclude_unset=True).items():
            setattr(template, field, value)
        
        db.commit()
        db.refresh(template)
        
        return ModelloTicketResponse.from_orm(template)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore aggiornamento template ticket: {str(e)}")

@router.get("/categories")
async def get_template_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """
    Lista delle categorie disponibili per i template
    """
    try:
        # Categorie dinamiche dai template esistenti
        categories = db.query(ModelloTask.categoria).distinct().filter(
            ModelloTask.categoria.isnot(None),
            ModelloTask.is_active == True
        ).all()
        
        category_list = [cat[0] for cat in categories if cat[0]]
        
        return {
            "categories": category_list,
            "predefined": ["development", "testing", "documentation", "deployment", "support", "admin"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore recupero categorie: {str(e)}")
