from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.routes.auth import get_current_user_dep
from app.schemas.milestones import (
    MilestoneCreate, MilestoneUpdate, MilestoneResponse,
    MilestoneListItem, MilestoneDetailResponse
)
from app.models.commesse import Milestone, Commessa
from app.models.users import User

router = APIRouter(prefix="/api/v1/milestones", tags=["Milestone Management"])

@router.post("/", response_model=MilestoneResponse)
async def create_milestone(
    milestone_data: MilestoneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """
    Crea una nuova milestone per una commessa
    """
    try:
        # Verifica che la commessa esista
        commessa = db.query(Commessa).filter(Commessa.id == milestone_data.commessa_id).first()
        if not commessa:
            raise HTTPException(status_code=404, detail="Commessa non trovata")
        
        # Verifica ordine milestone (deve essere progressivo)
        max_ordine = db.query(Milestone).filter(
            Milestone.commessa_id == milestone_data.commessa_id
        ).count()
        
        db_milestone = Milestone(
            commessa_id=milestone_data.commessa_id,
            nome=milestone_data.nome,
            descrizione=milestone_data.descrizione,
            ordine=milestone_data.ordine or (max_ordine + 1),
            sla_days=milestone_data.sla_days or 7,
            warning_days=milestone_data.warning_days or 2,
            escalation_days=milestone_data.escalation_days or 1,
            auto_generate_tickets=milestone_data.auto_generate_tickets,
            template_data=milestone_data.template_data or {}
        )
        
        db.add(db_milestone)
        db.commit()
        db.refresh(db_milestone)
        
        return MilestoneResponse.from_orm(db_milestone)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore creazione milestone: {str(e)}")

@router.get("/", response_model=List[MilestoneListItem])
async def list_milestones(
    commessa_id: Optional[UUID] = Query(None, description="Filtra per commessa"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """
    Lista milestone con filtri
    """
    try:
        query = db.query(Milestone)
        
        if commessa_id:
            query = query.filter(Milestone.commessa_id == commessa_id)
        
        milestones = query.order_by(Milestone.ordine).offset(skip).limit(limit).all()
        
        return [MilestoneListItem.from_orm(m) for m in milestones]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore recupero milestone: {str(e)}")

@router.get("/{milestone_id}", response_model=MilestoneDetailResponse)
async def get_milestone_detail(
    milestone_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """
    Dettaglio milestone con ticket associati
    """
    try:
        milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
        if not milestone:
            raise HTTPException(status_code=404, detail="Milestone non trovata")
        
        return MilestoneDetailResponse.from_orm(milestone)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore recupero milestone: {str(e)}")

@router.patch("/{milestone_id}", response_model=MilestoneResponse)
async def update_milestone(
    milestone_id: UUID,
    milestone_update: MilestoneUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """
    Aggiorna una milestone esistente
    """
    try:
        milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
        if not milestone:
            raise HTTPException(status_code=404, detail="Milestone non trovata")
        
        # Aggiorna campi forniti
        for field, value in milestone_update.dict(exclude_unset=True).items():
            setattr(milestone, field, value)
        
        db.commit()
        db.refresh(milestone)
        
        return MilestoneResponse.from_orm(milestone)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore aggiornamento milestone: {str(e)}")

@router.delete("/{milestone_id}")
async def delete_milestone(
    milestone_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """
    Elimina una milestone (solo se non ha ticket associati)
    """
    try:
        milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
        if not milestone:
            raise HTTPException(status_code=404, detail="Milestone non trovata")
        
        # TODO: Verifica che non ci siano ticket associati
        
        db.delete(milestone)
        db.commit()
        
        return {"message": "Milestone eliminata con successo"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore eliminazione milestone: {str(e)}")

@router.post("/{milestone_id}/reorder")
async def reorder_milestones(
    milestone_id: UUID,
    new_order: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """
    Riordina le milestone di una commessa
    """
    try:
        milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
        if not milestone:
            raise HTTPException(status_code=404, detail="Milestone non trovata")
        
        old_order = milestone.ordine
        commessa_id = milestone.commessa_id
        
        # Riordina le altre milestone
        if new_order > old_order:
            # Sposta in giù
            db.query(Milestone).filter(
                Milestone.commessa_id == commessa_id,
                Milestone.ordine > old_order,
                Milestone.ordine <= new_order
            ).update({Milestone.ordine: Milestone.ordine - 1})
        else:
            # Sposta in su
            db.query(Milestone).filter(
                Milestone.commessa_id == commessa_id,
                Milestone.ordine >= new_order,
                Milestone.ordine < old_order
            ).update({Milestone.ordine: Milestone.ordine + 1})
        
        milestone.ordine = new_order
        db.commit()
        
        return {"message": "Milestone riordinata con successo"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore riordino milestone: {str(e)}")
