from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.routes.auth import get_current_user_dep
from app.schemas.templates import (
    TaskTemplateCreate, TaskTemplateUpdate, TaskTemplateResponse,
    TicketTemplateCreate, TicketTemplateUpdate, TicketTemplateResponse
)
from app.models.tipi_commesse import ModelloTask
from app.models.commesse import ModelloTicket
from app.models.users import User

router = APIRouter(prefix="/api/v1/templates", tags=["Template Management"])

# TICKET TEMPLATES
@router.post("/ticket-templates", response_model=TicketTemplateResponse)
async def create_ticket_template(
    template_data: TicketTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Crea un nuovo modello di ticket"""
    try:
        db_template = ModelloTicket(
            nome=template_data.nome,
            descrizione=template_data.descrizione,
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
        
        return TicketTemplateResponse.from_orm(db_template)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore creazione template ticket: {str(e)}")

@router.get("/ticket-templates", response_model=List[TicketTemplateResponse])
async def list_ticket_templates(
    is_active: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Lista modelli ticket"""
    try:
        query = db.query(ModelloTicket).filter(ModelloTicket.is_active == is_active)
        templates = query.offset(skip).limit(limit).all()
        return [TicketTemplateResponse.from_orm(t) for t in templates]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore recupero template ticket: {str(e)}")
