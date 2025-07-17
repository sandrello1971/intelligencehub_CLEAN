"""
Kit Commerciali Routes - Versione Minimale DB-Compatible
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from pydantic import BaseModel
from app.core.database import get_db

router = APIRouter(prefix="/kit-commerciali", tags=["Kit Commerciali"])

class KitCreate(BaseModel):
    nome: str
    descrizione: Optional[str] = None
    articolo_principale_id: Optional[int] = None
    attivo: bool = True

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "kit-commerciali"}

@router.get("/")
async def get_kits(db: Session = Depends(get_db)):
    """Lista kit commerciali dal DB"""
    try:
        query = text("""
        SELECT id, nome, descrizione, articolo_principale_id, attivo, created_at
        FROM kit_commerciali 
        ORDER BY created_at DESC
        """)
        
        result = db.execute(query)
        kits = []
        
        for row in result:
            kits.append({
                "id": row.id,
                "nome": row.nome,
                "descrizione": row.descrizione,
                "articolo_principale_id": row.articolo_principale_id,
                "attivo": row.attivo,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "articoli": []  # Vuoto per ora
            })
        
        return {
            "success": True,
            "count": len(kits),
            "kit_commerciali": kits
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/articoli-disponibili")
async def get_articoli_disponibili(db: Session = Depends(get_db)):
    """Lista articoli per i kit"""
    try:
        query = text("""
        SELECT id, codice, nome, descrizione, tipo_prodotto, attivo
        FROM articoli 
        WHERE attivo = true 
        ORDER BY codice
        """)
        
        result = db.execute(query)
        articoli = []
        
        for row in result:
            articoli.append({
                "id": row.id,
                "codice": row.codice,
                "nome": row.nome,
                "descrizione": row.descrizione,
                "tipo_prodotto": row.tipo_prodotto,
                "attivo": row.attivo
            })
        
        return {
            "success": True,
            "count": len(articoli),
            "articoli": articoli
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/articoli-compositi")
async def get_articoli_compositi(db: Session = Depends(get_db)):
    """Lista articoli compositi per articolo principale"""
    try:
        query = text("""
        SELECT id, codice, nome, descrizione
        FROM articoli 
        WHERE tipo_prodotto = 'composito' AND attivo = true 
        ORDER BY codice
        """)
        
        result = db.execute(query)
        compositi = []
        
        for row in result:
            compositi.append({
                "id": row.id,
                "codice": row.codice,
                "nome": row.nome,
                "descrizione": row.descrizione
            })
        
        return {
            "success": True,
            "count": len(compositi),
            "articoli_compositi": compositi
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/")
async def create_kit(kit_data: KitCreate, db: Session = Depends(get_db)):
    """Crea nuovo kit commerciale"""
    try:
        query = text("""
        INSERT INTO kit_commerciali (nome, descrizione, articolo_principale_id, attivo, created_at)
        VALUES (:nome, :descrizione, :articolo_principale_id, :attivo, CURRENT_TIMESTAMP)
        RETURNING id
        """)
        
        result = db.execute(query, {
            "nome": kit_data.nome,
            "descrizione": kit_data.descrizione,
            "articolo_principale_id": kit_data.articolo_principale_id,
            "attivo": kit_data.attivo
        })
        
        kit_id = result.scalar()
        db.commit()
        
        return {
            "success": True,
            "message": f"Kit '{kit_data.nome}' creato con successo",
            "kit_id": kit_id
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}

@router.delete("/{kit_id}")
async def delete_kit(kit_id: int, db: Session = Depends(get_db)):
    """Elimina kit commerciale"""
    try:
        # Verifica che il kit esista
        check_query = text("SELECT nome FROM kit_commerciali WHERE id = :kit_id")
        kit_check = db.execute(check_query, {"kit_id": kit_id}).first()
        
        if not kit_check:
            raise HTTPException(status_code=404, detail="Kit non trovato")
        
        # Elimina il kit (CASCADE eliminerà automaticamente kit_articoli)
        delete_query = text("DELETE FROM kit_commerciali WHERE id = :kit_id")
        db.execute(delete_query, {"kit_id": kit_id})
        db.commit()
        
        return {
            "success": True,
            "message": f"Kit '{kit_check.nome}' eliminato con successo"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}

@router.put("/{kit_id}")
async def update_kit(kit_id: int, kit_data: KitCreate, db: Session = Depends(get_db)):
    """Aggiorna kit commerciale"""
    try:
        # Verifica che il kit esista
        check_query = text("SELECT id FROM kit_commerciali WHERE id = :kit_id")
        if not db.execute(check_query, {"kit_id": kit_id}).first():
            raise HTTPException(status_code=404, detail="Kit non trovato")
        
        # Aggiorna il kit
        update_query = text("""
        UPDATE kit_commerciali 
        SET nome = :nome, descrizione = :descrizione, 
            articolo_principale_id = :articolo_principale_id, attivo = :attivo
        WHERE id = :kit_id
        """)
        
        db.execute(update_query, {
            "kit_id": kit_id,
            "nome": kit_data.nome,
            "descrizione": kit_data.descrizione,
            "articolo_principale_id": kit_data.articolo_principale_id,
            "attivo": kit_data.attivo
        })
        db.commit()
        
        return {
            "success": True,
            "message": f"Kit '{kit_data.nome}' aggiornato con successo"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
