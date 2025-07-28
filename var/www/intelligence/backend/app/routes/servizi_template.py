from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID

from app.core.database import get_db
from app.routes.auth import get_current_user_dep
from app.models.users import User

router = APIRouter(prefix="/api/v1/servizi-template", tags=["Servizi Template"])

class ServizioTemplateAssociation(BaseModel):
    articolo_id: int
    modello_ticket_id: Optional[UUID] = None

class ServizioWithTemplate(BaseModel):
    id: int
    codice: str
    nome: str
    descrizione: Optional[str]
    modello_ticket_id: Optional[UUID]
    modello_ticket_nome: Optional[str]

@router.get("/", response_model=List[ServizioWithTemplate])
async def get_servizi_with_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Lista servizi con i loro template associati"""
    try:
        query = text("""
        SELECT 
            a.id,
            a.codice,
            a.nome,
            a.descrizione,
            a.modello_ticket_id,
            mt.nome as modello_ticket_nome
        FROM articoli a
        LEFT JOIN modelli_ticket mt ON a.modello_ticket_id = mt.id
        WHERE a.attivo = true
        ORDER BY a.nome
        """)
        
        result = db.execute(query)
        servizi = []
        
        for row in result:
            servizi.append(ServizioWithTemplate(
                id=row.id,
                codice=row.codice,
                nome=row.nome,
                descrizione=row.descrizione,
                modello_ticket_id=row.modello_ticket_id,
                modello_ticket_nome=row.modello_ticket_nome
            ))
        
        return servizi
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore recupero servizi: {str(e)}")

@router.put("/{articolo_id}/template")
async def associate_template_to_servizio(
    articolo_id: int,
    association: ServizioTemplateAssociation,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Associa un template a un servizio"""
    try:
        # Verifica che l'articolo esista
        check_articolo = text("SELECT id FROM articoli WHERE id = :id")
        articolo = db.execute(check_articolo, {"id": articolo_id}).first()
        
        if not articolo:
            raise HTTPException(status_code=404, detail="Servizio non trovato")
        
        # Se modello_ticket_id è fornito, verifica che esista
        if association.modello_ticket_id:
            check_template = text("SELECT id FROM modelli_ticket WHERE id = :id")
            template = db.execute(check_template, {"id": str(association.modello_ticket_id)}).first()
            
            if not template:
                raise HTTPException(status_code=404, detail="Template ticket non trovato")
        
        # Aggiorna l'associazione
        update_query = text("""
        UPDATE articoli 
        SET modello_ticket_id = :template_id, updated_at = CURRENT_TIMESTAMP
        WHERE id = :articolo_id
        """)
        
        db.execute(update_query, {
            "template_id": str(association.modello_ticket_id) if association.modello_ticket_id else None,
            "articolo_id": articolo_id
        })
        
        db.commit()
        
        return {
            "success": True,
            "message": "Associazione aggiornata con successo",
            "articolo_id": articolo_id,
            "modello_ticket_id": str(association.modello_ticket_id) if association.modello_ticket_id else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore associazione: {str(e)}")
