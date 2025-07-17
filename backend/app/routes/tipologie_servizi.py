
"""
Tipologie Servizi Routes - API per gestione tipologie servizi
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from pydantic import BaseModel
from app.core.database import get_db

router = APIRouter(prefix="/tipologie-servizi", tags=["Tipologie Servizi"])

class TipologiaCreate(BaseModel):
    nome: str
    descrizione: Optional[str] = None
    colore: Optional[str] = "#3B82F6"
    icona: Optional[str] = "📋"
    attivo: bool = True

class TipologiaUpdate(BaseModel):
    nome: Optional[str] = None
    descrizione: Optional[str] = None
    colore: Optional[str] = None
    icona: Optional[str] = None
    attivo: Optional[bool] = None

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "tipologie-servizi"}

@router.get("/")
async def get_tipologie(
    attivo: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Lista tutte le tipologie servizi"""
    try:
        where_clause = ""
        params = {}
        
        if attivo is not None:
            where_clause = "WHERE attivo = :attivo"
            params["attivo"] = attivo
        
        query = text(f"""
        SELECT id, nome, descrizione, colore, icona, attivo, created_at
        FROM tipologie_servizi 
        {where_clause}
        ORDER BY nome
        """)
        
        result = db.execute(query, params)
        tipologie = []
        
        for row in result:
            tipologie.append({
                "id": row.id,
                "nome": row.nome,
                "descrizione": row.descrizione,
                "colore": row.colore,
                "icona": row.icona,
                "attivo": row.attivo,
                "created_at": row.created_at.isoformat() if row.created_at else None
            })
        
        return {
            "success": True,
            "count": len(tipologie),
            "tipologie": tipologie
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/")
async def create_tipologia(tipologia_data: TipologiaCreate, db: Session = Depends(get_db)):
    """Crea nuova tipologia servizio"""
    try:
        # Verifica che il nome non esista già
        check_query = text("SELECT id FROM tipologie_servizi WHERE nome = :nome")
        existing = db.execute(check_query, {"nome": tipologia_data.nome}).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Nome tipologia già esistente")
        
        # Inserisci nuova tipologia
        insert_query = text("""
        INSERT INTO tipologie_servizi (nome, descrizione, colore, icona, attivo, created_at)
        VALUES (:nome, :descrizione, :colore, :icona, :attivo, CURRENT_TIMESTAMP)
        RETURNING id
        """)
        
        result = db.execute(insert_query, {
            "nome": tipologia_data.nome,
            "descrizione": tipologia_data.descrizione,
            "colore": tipologia_data.colore,
            "icona": tipologia_data.icona,
            "attivo": tipologia_data.attivo
        })
        
        tipologia_id = result.scalar()
        db.commit()
        
        return {
            "success": True,
            "message": f"Tipologia '{tipologia_data.nome}' creata con successo",
            "tipologia_id": tipologia_id
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}

@router.put("/{tipologia_id}")
async def update_tipologia(
    tipologia_id: int, 
    tipologia_data: TipologiaUpdate, 
    db: Session = Depends(get_db)
):
    """Aggiorna tipologia servizio"""
    try:
        # Verifica che la tipologia esista
        check_query = text("SELECT nome FROM tipologie_servizi WHERE id = :id")
        existing = db.execute(check_query, {"id": tipologia_id}).first()
        
        if not existing:
            raise HTTPException(status_code=404, detail="Tipologia non trovata")
        
        # Costruisci query dinamica per aggiornare solo i campi forniti
        update_fields = []
        params = {"id": tipologia_id}
        
        for field, value in tipologia_data.dict(exclude_unset=True).items():
            if value is not None:
                update_fields.append(f"{field} = :{field}")
                params[field] = value
        
        if not update_fields:
            return {"success": True, "message": "Nessuna modifica da applicare"}
        
        update_query = text(f"""
        UPDATE tipologie_servizi 
        SET {', '.join(update_fields)}
        WHERE id = :id
        """)
        
        db.execute(update_query, params)
        db.commit()
        
        return {
            "success": True,
            "message": f"Tipologia aggiornata con successo"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}

@router.delete("/{tipologia_id}")
async def delete_tipologia(tipologia_id: int, db: Session = Depends(get_db)):
    """Elimina tipologia servizio"""
    try:
        # Verifica che la tipologia esista
        check_query = text("SELECT nome FROM tipologie_servizi WHERE id = :id")
        tipologia = db.execute(check_query, {"id": tipologia_id}).first()
        
        if not tipologia:
            raise HTTPException(status_code=404, detail="Tipologia non trovata")
        
        # Verifica che non ci siano articoli che usano questa tipologia
        usage_query = text("SELECT COUNT(*) as count FROM articoli WHERE tipologia_servizio_id = :id")
        usage = db.execute(usage_query, {"id": tipologia_id}).first()
        
        if usage.count > 0:
            raise HTTPException(
                status_code=400, 
                detail=f"Impossibile eliminare: {usage.count} articoli utilizzano questa tipologia"
            )
        
        # Elimina la tipologia
        delete_query = text("DELETE FROM tipologie_servizi WHERE id = :id")
        db.execute(delete_query, {"id": tipologia_id})
        db.commit()
        
        return {
            "success": True,
            "message": f"Tipologia '{tipologia.nome}' eliminata con successo"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}

@router.get("/{tipologia_id}")
async def get_tipologia(tipologia_id: int, db: Session = Depends(get_db)):
    """Ottieni singola tipologia per ID"""
    try:
        query = text("""
        SELECT id, nome, descrizione, colore, icona, attivo, created_at
        FROM tipologie_servizi 
        WHERE id = :id
        """)
        
        result = db.execute(query, {"id": tipologia_id}).first()
        
        if not result:
            raise HTTPException(status_code=404, detail="Tipologia non trovata")
        
        tipologia = {
            "id": result.id,
            "nome": result.nome,
            "descrizione": result.descrizione,
            "colore": result.colore,
            "icona": result.icona,
            "attivo": result.attivo,
            "created_at": result.created_at.isoformat() if result.created_at else None
        }
        
        return {"success": True, "tipologia": tipologia}
    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "error": str(e)}
