
"""
Partner Routes - API per gestione partner e servizi erogabili
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from pydantic import BaseModel
from app.core.database import get_db

router = APIRouter(prefix="/partner", tags=["Partner"])

class PartnerCreate(BaseModel):
    nome: str
    ragione_sociale: Optional[str] = None
    partita_iva: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    sito_web: Optional[str] = None
    indirizzo: Optional[str] = None
    note: Optional[str] = None
    attivo: bool = True

class PartnerUpdate(BaseModel):
    nome: Optional[str] = None
    ragione_sociale: Optional[str] = None
    partita_iva: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    sito_web: Optional[str] = None
    indirizzo: Optional[str] = None
    note: Optional[str] = None
    attivo: Optional[bool] = None

class PartnerServizioCreate(BaseModel):
    articolo_id: int
    prezzo_partner: Optional[float] = None
    note: Optional[str] = None

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "partner"}

@router.get("/")
async def get_partner(
    attivo: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lista tutti i partner"""
    try:
        where_conditions = []
        params = {}
        
        if attivo is not None:
            where_conditions.append("p.attivo = :attivo")
            params["attivo"] = attivo
        
        if search:
            where_conditions.append("(p.nome ILIKE :search OR p.ragione_sociale ILIKE :search)")
            params["search"] = f"%{search}%"
        
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        query = text(f"""
        SELECT p.id, p.nome, p.ragione_sociale, p.partita_iva, p.email, 
               p.telefono, p.sito_web, p.indirizzo, p.note, p.attivo, p.created_at,
               COUNT(ps.articolo_id) as servizi_count
        FROM partner p
        LEFT JOIN partner_servizi ps ON p.id = ps.partner_id
        {where_clause}
        GROUP BY p.id, p.nome, p.ragione_sociale, p.partita_iva, p.email, 
                 p.telefono, p.sito_web, p.indirizzo, p.note, p.attivo, p.created_at
        ORDER BY p.nome
        """)
        
        result = db.execute(query, params)
        partner = []
        
        for row in result:
            partner.append({
                "id": row.id,
                "nome": row.nome,
                "ragione_sociale": row.ragione_sociale,
                "partita_iva": row.partita_iva,
                "email": row.email,
                "telefono": row.telefono,
                "sito_web": row.sito_web,
                "indirizzo": row.indirizzo,
                "note": row.note,
                "attivo": row.attivo,
                "servizi_count": row.servizi_count,
                "created_at": row.created_at.isoformat() if row.created_at else None
            })
        
        return {
            "success": True,
            "count": len(partner),
            "partner": partner
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/")
async def create_partner(partner_data: PartnerCreate, db: Session = Depends(get_db)):
    """Crea nuovo partner"""
    try:
        # Verifica che il nome non esista già
        check_query = text("SELECT id FROM partner WHERE nome = :nome")
        existing = db.execute(check_query, {"nome": partner_data.nome}).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Nome partner già esistente")
        
        # Inserisci nuovo partner
        insert_query = text("""
        INSERT INTO partner (nome, ragione_sociale, partita_iva, email, telefono, 
                           sito_web, indirizzo, note, attivo, created_at, updated_at)
        VALUES (:nome, :ragione_sociale, :partita_iva, :email, :telefono,
                :sito_web, :indirizzo, :note, :attivo, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        RETURNING id
        """)
        
        result = db.execute(insert_query, partner_data.dict())
        partner_id = result.scalar()
        db.commit()
        
        return {
            "success": True,
            "message": f"Partner '{partner_data.nome}' creato con successo",
            "partner_id": partner_id
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}

@router.get("/{partner_id}/servizi")
async def get_partner_servizi(partner_id: int, db: Session = Depends(get_db)):
    """Ottieni servizi erogabili da un partner"""
    try:
        query = text("""
        SELECT ps.id, ps.prezzo_partner, ps.note, ps.created_at,
               a.id as articolo_id, a.codice, a.nome as articolo_nome, 
               a.descrizione as articolo_descrizione, a.tipo_prodotto,
               ts.nome as tipologia_nome, ts.colore as tipologia_colore, ts.icona as tipologia_icona
        FROM partner_servizi ps
        JOIN articoli a ON ps.articolo_id = a.id
        LEFT JOIN tipologie_servizi ts ON a.tipologia_servizio_id = ts.id
        WHERE ps.partner_id = :partner_id AND a.attivo = true
        ORDER BY a.nome
        """)
        
        result = db.execute(query, {"partner_id": partner_id})
        servizi = []
        
        for row in result:
            servizi.append({
                "id": row.id,
                "articolo_id": row.articolo_id,
                "articolo_codice": row.codice,
                "articolo_nome": row.articolo_nome,
                "articolo_descrizione": row.articolo_descrizione,
                "tipo_prodotto": row.tipo_prodotto,
                "tipologia_nome": row.tipologia_nome,
                "tipologia_colore": row.tipologia_colore,
                "tipologia_icona": row.tipologia_icona,
                "prezzo_partner": float(row.prezzo_partner) if row.prezzo_partner else None,
                "note": row.note,
                "created_at": row.created_at.isoformat() if row.created_at else None
            })
        
        return {
            "success": True,
            "count": len(servizi),
            "servizi": servizi
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/{partner_id}/servizi")
async def add_servizio_to_partner(
    partner_id: int, 
    servizio_data: PartnerServizioCreate, 
    db: Session = Depends(get_db)
):
    """Aggiungi servizio erogabile a un partner"""
    try:
        # Verifica che il partner esista
        partner_check = db.execute(
            text("SELECT nome FROM partner WHERE id = :id AND attivo = true"),
            {"id": partner_id}
        ).first()
        
        if not partner_check:
            raise HTTPException(status_code=404, detail="Partner non trovato")
        
        # Verifica che l'articolo esista
        articolo_check = db.execute(
            text("SELECT nome FROM articoli WHERE id = :id AND attivo = true"),
            {"id": servizio_data.articolo_id}
        ).first()
        
        if not articolo_check:
            raise HTTPException(status_code=404, detail="Articolo non trovato")
        
        # Verifica che non esista già questa associazione
        existing = db.execute(
            text("SELECT id FROM partner_servizi WHERE partner_id = :partner_id AND articolo_id = :articolo_id"),
            {"partner_id": partner_id, "articolo_id": servizio_data.articolo_id}
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Servizio già associato a questo partner")
        
        # Inserisci associazione
        insert_query = text("""
        INSERT INTO partner_servizi (partner_id, articolo_id, prezzo_partner, note, created_at)
        VALUES (:partner_id, :articolo_id, :prezzo_partner, :note, CURRENT_TIMESTAMP)
        RETURNING id
        """)
        
        result = db.execute(insert_query, {
            "partner_id": partner_id,
            "articolo_id": servizio_data.articolo_id,
            "prezzo_partner": servizio_data.prezzo_partner,
            "note": servizio_data.note
        })
        
        servizio_id = result.scalar()
        db.commit()
        
        return {
            "success": True,
            "message": f"Servizio '{articolo_check.nome}' aggiunto al partner '{partner_check.nome}'",
            "servizio_id": servizio_id
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}

@router.delete("/{partner_id}/servizi/{servizio_id}")
async def remove_servizio_from_partner(
    partner_id: int, 
    servizio_id: int, 
    db: Session = Depends(get_db)
):
    """Rimuovi servizio erogabile da un partner"""
    try:
        # Verifica che l'associazione esista
        check_query = text("""
        SELECT ps.id, a.nome as articolo_nome, p.nome as partner_nome
        FROM partner_servizi ps
        JOIN articoli a ON ps.articolo_id = a.id
        JOIN partner p ON ps.partner_id = p.id
        WHERE ps.id = :servizio_id AND ps.partner_id = :partner_id
        """)
        
        associazione = db.execute(check_query, {
            "servizio_id": servizio_id,
            "partner_id": partner_id
        }).first()
        
        if not associazione:
            raise HTTPException(status_code=404, detail="Associazione non trovata")
        
        # Elimina associazione
        delete_query = text("DELETE FROM partner_servizi WHERE id = :servizio_id AND partner_id = :partner_id")
        db.execute(delete_query, {"servizio_id": servizio_id, "partner_id": partner_id})
        db.commit()
        
        return {
            "success": True,
            "message": f"Servizio '{associazione.articolo_nome}' rimosso dal partner '{associazione.partner_nome}'"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}

@router.get("/by-servizio/{articolo_id}")
async def get_partner_by_servizio(articolo_id: int, db: Session = Depends(get_db)):
    """Ottieni partner che erogano un servizio specifico"""
    try:
        query = text("""
        SELECT p.id, p.nome, p.ragione_sociale, p.email, p.telefono,
               ps.prezzo_partner, ps.note
        FROM partner p
        JOIN partner_servizi ps ON p.id = ps.partner_id
        WHERE ps.articolo_id = :articolo_id AND p.attivo = true
        ORDER BY p.nome
        """)
        
        result = db.execute(query, {"articolo_id": articolo_id})
        partner = []
        
        for row in result:
            partner.append({
                "id": row.id,
                "nome": row.nome,
                "ragione_sociale": row.ragione_sociale,
                "email": row.email,
                "telefono": row.telefono,
                "prezzo_partner": float(row.prezzo_partner) if row.prezzo_partner else None,
                "note": row.note
            })
        
        return {
            "success": True,
            "count": len(partner),
            "partner": partner
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
