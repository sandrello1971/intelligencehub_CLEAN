from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.core.database import get_db
from app.routes.auth import get_current_user_dep
from app.schemas.commesse import (
    CommessaCreate, CommessaUpdate, CommessaResponse, 
    CommessaListItem, CommessaDetailResponse
)
from app.models.commesse import Commessa
from app.models.users import User

router = APIRouter(prefix="/api/v1/commesse", tags=["Commesse Management"])

@router.post("/", response_model=CommessaResponse)
async def create_commessa(
    commessa_data: CommessaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """
    Crea una nuova commessa
    """
    try:
        # Verifica che il codice non esista già
        existing = db.query(Commessa).filter(Commessa.codice == commessa_data.codice).first()
        if existing:
            raise HTTPException(status_code=400, detail="Codice commessa già esistente")
        
        # Crea nuova commessa
        db_commessa = Commessa(
            codice=commessa_data.codice,
            nome=commessa_data.nome,
            descrizione=commessa_data.descrizione,
            client_id=commessa_data.client_id,
            owner_id=commessa_data.owner_id or current_user.id,
            budget=commessa_data.budget,
            data_inizio=commessa_data.data_inizio,
            data_fine_prevista=commessa_data.data_fine_prevista,
            sla_default_hours=commessa_data.sla_default_hours or 48,
            metadata=commessa_data.metadata or {}
        )
        
        db.add(db_commessa)
        db.commit()
        db.refresh(db_commessa)
        
        return CommessaResponse.from_orm(db_commessa)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore creazione commessa: {str(e)}")

@router.get("/", response_model=List[CommessaListItem])
async def list_commesse(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None),
    client_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """
    Lista tutte le commesse con filtri
    """
    try:
        query = db.query(Commessa)
        
        # Applica filtri
        if status:
            query = query.filter(Commessa.status == status)
        if client_id:
            query = query.filter(Commessa.client_id == client_id)
        
        # Paginazione
        commesse = query.offset(skip).limit(limit).all()
        
        return [CommessaListItem.from_orm(c) for c in commesse]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore recupero commesse: {str(e)}")

@router.get("/{commessa_id}", response_model=CommessaDetailResponse)
async def get_commessa_detail(
    commessa_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """
    Dettaglio commessa con milestone e tickets associati
    """
    try:
        commessa = db.query(Commessa).filter(Commessa.id == commessa_id).first()
        if not commessa:
            raise HTTPException(status_code=404, detail="Commessa non trovata")
        
        return CommessaDetailResponse.from_orm(commessa)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore recupero commessa: {str(e)}")

@router.patch("/{commessa_id}", response_model=CommessaResponse)
async def update_commessa(
    commessa_id: str,
    commessa_update: CommessaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """
    Aggiorna una commessa esistente
    """
    try:
        commessa = db.query(Commessa).filter(Commessa.id == commessa_id).first()
        if not commessa:
            raise HTTPException(status_code=404, detail="Commessa non trovata")
        
        # Aggiorna campi forniti
        for field, value in commessa_update.dict(exclude_unset=True).items():
            setattr(commessa, field, value)
        
        db.commit()
        db.refresh(commessa)
        
        return CommessaResponse.from_orm(commessa)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore aggiornamento commessa: {str(e)}")

@router.delete("/{commessa_id}")
async def delete_commessa(
    commessa_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """
    Elimina una commessa (solo se non ha ticket associati)
    """
    try:
        commessa = db.query(Commessa).filter(Commessa.id == commessa_id).first()
        if not commessa:
            raise HTTPException(status_code=404, detail="Commessa non trovata")
        
        # Verifica che non ci siano tickets associati
        # TODO: Aggiungere check per tickets associati
        
        db.delete(commessa)
        db.commit()
        
        return {"message": "Commessa eliminata con successo"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore eliminazione commessa: {str(e)}")

@router.post("/{commessa_id}/close")
async def close_commessa(
    commessa_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """
    Chiude una commessa
    """
    try:
        commessa = db.query(Commessa).filter(Commessa.id == commessa_id).first()
        if not commessa:
            raise HTTPException(status_code=404, detail="Commessa non trovata")
        
        commessa.status = "closed"
        db.commit()
        
        return {"message": "Commessa chiusa con successo"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore chiusura commessa: {str(e)}")
