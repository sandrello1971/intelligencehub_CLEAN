from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
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


@router.get("/ticket-templates/{template_id}", response_model=TicketTemplateResponse)
async def get_ticket_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Recupera singolo modello ticket"""
    try:
        from uuid import UUID
        template_uuid = UUID(template_id)
        template = db.query(ModelloTicket).filter(ModelloTicket.id == template_uuid).first()
        
        if not template:
            raise HTTPException(status_code=404, detail="Template ticket non trovato")
        
        return TicketTemplateResponse.from_orm(template)
        
    except ValueError:
        raise HTTPException(status_code=400, detail="ID template non valido")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore recupero template: {str(e)}")


@router.put("/ticket-templates/{template_id}", response_model=TicketTemplateResponse)
async def update_ticket_template(
    template_id: str,
    template_data: TicketTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Aggiorna modello ticket esistente"""
    try:
        from uuid import UUID
        template_uuid = UUID(template_id)
        
        # Trova il template esistente
        db_template = db.query(ModelloTicket).filter(ModelloTicket.id == template_uuid).first()
        if not db_template:
            raise HTTPException(status_code=404, detail="Template ticket non trovato")
        
        # Aggiorna solo i campi forniti
        update_data = template_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_template, field):
                setattr(db_template, field, value)
        
        # Imposta updated_at
        from datetime import datetime
        db_template.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_template)
        
        return TicketTemplateResponse.from_orm(db_template)
        
    except ValueError:
        raise HTTPException(status_code=400, detail="ID template non valido")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore aggiornamento template: {str(e)}")


@router.delete("/ticket-templates/{template_id}")
async def delete_ticket_template(
    template_id: str,
    hard_delete: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Elimina modello ticket (soft delete di default)"""
    try:
        from uuid import UUID
        template_uuid = UUID(template_id)
        
        # Trova il template esistente
        db_template = db.query(ModelloTicket).filter(ModelloTicket.id == template_uuid).first()
        if not db_template:
            raise HTTPException(status_code=404, detail="Template ticket non trovato")
        
        if hard_delete:
            # Eliminazione fisica
            db.delete(db_template)
            message = "Template eliminato definitivamente"
        else:
            # Soft delete - disattiva il template
            db_template.is_active = False
            from datetime import datetime
            db_template.updated_at = datetime.utcnow()
            message = "Template disattivato con successo"
        
        db.commit()
        
        return {
            "success": True,
            "message": message,
            "template_id": str(template_id),
            "hard_delete": hard_delete
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="ID template non valido")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore eliminazione template: {str(e)}")


@router.post("/ticket-templates/{template_id}/activate")
async def activate_ticket_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Riattiva un template disattivato"""
    try:
        from uuid import UUID
        template_uuid = UUID(template_id)
        
        db_template = db.query(ModelloTicket).filter(ModelloTicket.id == template_uuid).first()
        if not db_template:
            raise HTTPException(status_code=404, detail="Template ticket non trovato")
        
        db_template.is_active = True
        from datetime import datetime
        db_template.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "success": True,
            "message": "Template riattivato con successo",
            "template_id": str(template_id)
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="ID template non valido")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore riattivazione template: {str(e)}")
