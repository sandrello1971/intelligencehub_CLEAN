# routes/admin/tipi_commesse.py
# API Routes per gestione Tipi Commesse - IntelligenceHUB

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import csv
import io
import tempfile
import os
from datetime import datetime

from app.database import get_db
from app.models.admin import TipoCommessa, TipoCommessaCreate, TipoCommessaUpdate
from app.services.admin.tipi_commesse_service import TipiCommesseService
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/admin/tipi-commesse", tags=["admin", "tipi-commesse"])

# Dependency injection
def get_tipi_commesse_service(db: Session = Depends(get_db)) -> TipiCommesseService:
    return TipiCommesseService(db)

@router.get("/", response_model=List[TipoCommessa])
async def get_all_tipi_commesse(
    search: Optional[str] = Query(None, description="Ricerca per nome o codice"),
    is_active: Optional[bool] = Query(None, description="Filtra per stato attivo"),
    page: int = Query(1, ge=1, description="Numero pagina"),
    per_page: int = Query(20, ge=1, le=100, description="Elementi per pagina"),
    service: TipiCommesseService = Depends(get_tipi_commesse_service),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera tutti i tipi commesse con filtri opzionali e paginazione
    """
    try:
        if page == 1 and per_page == 20 and not search and is_active is None:
            # Chiamata semplice senza paginazione per compatibilità
            return service.get_all()
        else:
            # Chiamata con paginazione
            result = service.get_paginated(
                page=page,
                per_page=per_page,
                search=search,
                is_active=is_active
            )
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore recupero tipi commesse: {str(e)}")

@router.get("/stats")
async def get_tipi_commesse_stats(
    service: TipiCommesseService = Depends(get_tipi_commesse_service),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera statistiche sui tipi commesse
    """
    try:
        return service.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore recupero statistiche: {str(e)}")

@router.get("/check-code")
async def check_code_availability(
    code: str = Query(..., description="Codice da verificare"),
    exclude_id: Optional[str] = Query(None, description="ID da escludere dal controllo"),
    service: TipiCommesseService = Depends(get_tipi_commesse_service),
    current_user: User = Depends(get_current_user)
):
    """
    Verifica disponibilità codice tipo commessa
    """
    try:
        available = service.check_code_availability(code, exclude_id)
        return {"available": available}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore verifica codice: {str(e)}")

@router.get("/{tipo_commessa_id}", response_model=TipoCommessa)
async def get_tipo_commessa_by_id(
    tipo_commessa_id: str,
    service: TipiCommesseService = Depends(get_tipi_commesse_service),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera tipo commessa per ID
    """
    try:
        tipo_commessa = service.get_by_id(tipo_commessa_id)
        if not tipo_commessa:
            raise HTTPException(status_code=404, detail="Tipo commessa non trovato")
        return tipo_commessa
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore recupero tipo commessa: {str(e)}")

@router.post("/", response_model=TipoCommessa, status_code=201)
async def create_tipo_commessa(
    tipo_commessa_data: TipoCommessaCreate,
    service: TipiCommesseService = Depends(get_tipi_commesse_service),
    current_user: User = Depends(get_current_user)
):
    """
    Crea nuovo tipo commessa
    """
    try:
        # Verifica codice univoco
        if not service.check_code_availability(tipo_commessa_data.codice):
            raise HTTPException(status_code=400, detail="Codice già esistente")
        
        return service.create(tipo_commessa_data, current_user.id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore creazione tipo commessa: {str(e)}")

@router.put("/{tipo_commessa_id}", response_model=TipoCommessa)
async def update_tipo_commessa(
    tipo_commessa_id: str,
    tipo_commessa_data: TipoCommessaUpdate,
    service: TipiCommesseService = Depends(get_tipi_commesse_service),
    current_user: User = Depends(get_current_user)
):
    """
    Aggiorna tipo commessa esistente
    """
    try:
        # Verifica esistenza
        existing = service.get_by_id(tipo_commessa_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Tipo commessa non trovato")
        
        # Verifica codice univoco se modificato
        if tipo_commessa_data.codice and tipo_commessa_data.codice != existing.codice:
            if not service.check_code_availability(tipo_commessa_data.codice, tipo_commessa_id):
                raise HTTPException(status_code=400, detail="Codice già esistente")
        
        return service.update(tipo_commessa_id, tipo_commessa_data, current_user.id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore aggiornamento tipo commessa: {str(e)}")

@router.delete("/{tipo_commessa_id}")
async def delete_tipo_commessa(
    tipo_commessa_id: str,
    service: TipiCommesseService = Depends(get_tipi_commesse_service),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina tipo commessa
    """
    try:
        # Verifica esistenza
        existing = service.get_by_id(tipo_commessa_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Tipo commessa non trovato")
        
        # Verifica che non sia in uso
        if service.is_in_use(tipo_commessa_id):
            raise HTTPException(status_code=400, detail="Impossibile eliminare: tipo commessa in uso")
        
        service.delete(tipo_commessa_id)
        return {"message": "Tipo commessa eliminato con successo"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore eliminazione tipo commessa: {str(e)}")

@router.patch("/{tipo_commessa_id}/toggle-active", response_model=TipoCommessa)
async def toggle_active_tipo_commessa(
    tipo_commessa_id: str,
    toggle_data: dict,
    service: TipiCommesseService = Depends(get_tipi_commesse_service),
    current_user: User = Depends(get_current_user)
):
    """
    Attiva/disattiva tipo commessa
    """
    try:
        # Verifica esistenza
        existing = service.get_by_id(tipo_commessa_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Tipo commessa non trovato")
        
        is_active = toggle_data.get("is_active", not existing.is_active)
        return service.toggle_active(tipo_commessa_id, is_active, current_user.id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore toggle attivazione: {str(e)}")

@router.post("/{tipo_commessa_id}/duplicate", response_model=TipoCommessa)
async def duplicate_tipo_commessa(
    tipo_commessa_id: str,
    duplicate_data: dict,
    service: TipiCommesseService = Depends(get_tipi_commesse_service),
    current_user: User = Depends(get_current_user)
):
    """
    Duplica tipo commessa esistente
    """
    try:
        # Verifica esistenza
        existing = service.get_by_id(tipo_commessa_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Tipo commessa non trovato")
        
        new_name = duplicate_data.get("new_name")
        return service.duplicate(tipo_commessa_id, new_name, current_user.id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore duplicazione tipo commessa: {str(e)}")

@router.get("/export/csv")
async def export_tipi_commesse_csv(
    service: TipiCommesseService = Depends(get_tipi_commesse_service),
    current_user: User = Depends(get_current_user)
):
    """
    Esporta tipi commesse in formato CSV
    """
    try:
        csv_data = service.export_to_csv()
        
        # Crea file temporaneo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tipi_commesse_{timestamp}.csv"
        
        # Simula download URL (in produzione usare storage cloud)
        download_url = f"/api/v1/downloads/{filename}"
        
        return {"download_url": download_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore esportazione CSV: {str(e)}")

@router.post("/import/csv")
async def import_tipi_commesse_csv(
    file: UploadFile = File(...),
    service: TipiCommesseService = Depends(get_tipi_commesse_service),
    current_user: User = Depends(get_current_user)
):
    """
    Importa tipi commesse da file CSV
    """
    try:
        # Verifica tipo file
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File deve essere in formato CSV")
        
        # Leggi contenuto file
        contents = await file.read()
        csv_data = contents.decode('utf-8')
        
        # Processa import
        result = service.import_from_csv(csv_data, current_user.id)
        
        return {
            "imported": result["imported"],
            "errors": result["errors"],
            "message": f"Importati {result['imported']} tipi commesse"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore importazione CSV: {str(e)}")

# Health check endpoint
@router.get("/health")
async def health_check():
    """
    Health check per API tipi commesse
    """
    return {
        "status": "healthy",
        "service": "tipi_commesse",
        "timestamp": datetime.now().isoformat()
    }
