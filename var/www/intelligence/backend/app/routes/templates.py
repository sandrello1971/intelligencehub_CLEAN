from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.schemas.templates import (
    ModelloTaskCreate, ModelloTaskUpdate, ModelloTaskResponse,
    CreateUpdate, ModelloTicketResponse,
    TemplateListItem
)
from app.models.tipi_commesse import ModelloTask
from app.models.milestone import Milestone
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

@router.post("/ticket-templates", response_model=Response)
async def create_ticket_template(
    template_data: Create,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """
    Crea un nuovo modello di ticket
    """
    try:
        # Verifica che la milestone esista se specificata
        
        db_template = ModelloTask(
            nome=template_data.nome,
            descrizione=template_data.descrizione,
            articolo_id=template_data.articolo_id,
            workflow_template_id=template_data.workflow_template_id,
            priority=template_data.priority,
            sla_hours=template_data.sla_hours,
            auto_assign_rules=template_data.auto_assign_rules or {},
            template_description=template_data.template_description,
            is_active=template_data.is_active
        )
        
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        
        return Response.from_orm(db_template)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore creazione template ticket: {str(e)}")

@router.get("/ticket-templates", response_model=List[Response])
async def list_ticket_templates(
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
        query = db.query().filter(ModelloTicket.is_active == is_active)
        
        
        templates = query.offset(skip).limit(limit).all()
        
        return [Response.from_orm(t) for t in templates]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore recupero template ticket: {str(e)}")

@router.patch("/ticket-templates/{template_id}", response_model=Response)
async def update_ticket_template(
    template_id: UUID,
    template_update: Update,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """
    Aggiorna un modello ticket
    """
    try:
        template = db.query().filter(ModelloTicket.id == template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="Template ticket non trovato")
        
        # Aggiorna campi forniti
        for field, value in template_update.dict(exclude_unset=True).items():
            setattr(template, field, value)
        
        db.commit()
        db.refresh(template)
        
        return Response.from_orm(template)
        
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

@router.get("/ticket-templates/{template_id}", response_model=Response)
async def get_ticket_template(
    template_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """
    Recupera un singolo modello ticket
    """
    try:
        template = db.query().filter(ModelloTicket.id == template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="Template ticket non trovato")
        
        return Response.from_orm(template)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore recupero template ticket: {str(e)}")

@router.patch("/ticket-templates/{template_id}", response_model=Response)
async def update_ticket_template(
    template_id: UUID,
    template_update: Update,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """
    Aggiorna un modello ticket
    """
    try:
        template = db.query().filter(ModelloTicket.id == template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="Template ticket non trovato")
        
        # Aggiorna campi forniti
        for field, value in template_update.dict(exclude_unset=True).items():
            setattr(template, field, value)
        
        db.commit()
        db.refresh(template)
        
        return Response.from_orm(template)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore aggiornamento template ticket: {str(e)}")

@router.delete("/ticket-templates/{template_id}")
async def delete_ticket_template(
    template_id: UUID,
    hard_delete: bool = Query(False, description="Elimina definitivamente invece di disattivare"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """
    Elimina un modello ticket (soft delete per default)
    """
    try:
        template = db.query().filter(ModelloTicket.id == template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="Template ticket non trovato")
        
        if hard_delete:
            # Elimina definitivamente
            db.delete(template)
            message = "Template ticket eliminato definitivamente"
        else:
            # Soft delete (disattiva)
            template.is_active = False
            message = "Template ticket disattivato con successo"
        
        db.commit()
        
        return {"message": message}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore eliminazione template ticket: {str(e)}")

@router.post("/ticket-templates/{template_id}/clone", response_model=Response)
async def clone_ticket_template(
    template_id: UUID,
    new_name: str = Query(..., description="Nome per il nuovo template clonato"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """
    Clona un modello ticket esistente
    """
    try:
        # Trova il template sorgente
        source_template = db.query().filter(ModelloTicket.id == template_id).first()
        if not source_template:
            raise HTTPException(status_code=404, detail="Template ticket sorgente non trovato")
        
        # Crea il nuovo template clonato
        cloned_template = (
            nome=new_name,
            descrizione=f"Copia di: {source_template.descrizione}" if source_template.descrizione else None,
            articolo_id=source_template.articolo_id,
            workflow_template_id=source_template.workflow_template_id,
            priority=source_template.priority,
            sla_hours=source_template.sla_hours,
            auto_assign_rules=source_template.auto_assign_rules or {},
            template_description=source_template.template_description,
            is_active=True
        )
        
        db.add(cloned_template)
        db.commit()
        db.refresh(cloned_template)
        
        return Response.from_orm(cloned_template)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore clonazione template ticket: {str(e)}")
