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

class KitArticoloCreate(BaseModel):
    articolo_id: int
    quantita: int = 1
    obbligatorio: bool = False
    ordine: int = 0

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "kit-commerciali"}

@router.get("/")
# Sostituisci l'endpoint GET "/" nel file kit_commerciali.py con questo:

@router.get("/")
async def get_kits(db: Session = Depends(get_db)):
    """Lista kit commerciali dal DB con articoli"""
    try:
        # Query principale per i kit
        kits_query = text("""
        SELECT id, nome, descrizione, articolo_principale_id, attivo, created_at
        FROM kit_commerciali 
        ORDER BY created_at DESC
        """)
        
        kits_result = db.execute(kits_query)
        kits = []
        
        for kit_row in kits_result:
            # Query per gli articoli di questo kit
            articoli_query = text("""
                SELECT ka.id, ka.quantita, ka.obbligatorio, ka.ordine,
                       a.id as articolo_id, a.codice as articolo_codice, 
                       a.nome as articolo_nome
                FROM kit_articoli ka
                JOIN articoli a ON ka.articolo_id = a.id
                WHERE ka.kit_commerciale_id = :kit_id
                ORDER BY ka.ordine, ka.id
            """)
            
            articoli_result = db.execute(articoli_query, {"kit_id": kit_row.id})
            articoli = []
            
            for articolo_row in articoli_result:
                articoli.append({
                    "id": articolo_row.id,
                    "articolo_id": articolo_row.articolo_id,
                    "articolo_codice": articolo_row.articolo_codice,
                    "articolo_nome": articolo_row.articolo_nome,
                    "quantita": articolo_row.quantita,
                    "obbligatorio": articolo_row.obbligatorio,
                    "ordine": articolo_row.ordine
                })
            
            kits.append({
                "id": kit_row.id,
                "nome": kit_row.nome,
                "descrizione": kit_row.descrizione,
                "articolo_principale_id": kit_row.articolo_principale_id,
                "attivo": kit_row.attivo,
                "created_at": kit_row.created_at.isoformat() if kit_row.created_at else None,
                "articoli": articoli  # Ora contiene i servizi reali
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

@router.post("/{kit_id}/articoli")
async def add_articolo_to_kit(
    kit_id: int, 
    articolo_data: KitArticoloCreate,
    db: Session = Depends(get_db)
):
    """Aggiungi articolo a kit commerciale"""
    try:
        # Verifica che il kit esista
        kit_check = db.execute(text("SELECT id FROM kit_commerciali WHERE id = :kit_id"), 
                              {"kit_id": kit_id})
        if not kit_check.fetchone():
            raise HTTPException(status_code=404, detail="Kit non trovato")
            
        # Verifica che l'articolo esista
        articolo_check = db.execute(text("SELECT id, nome FROM articoli WHERE id = :articolo_id"), 
                                  {"articolo_id": articolo_data.articolo_id})
        articolo = articolo_check.fetchone()
        if not articolo:
            raise HTTPException(status_code=404, detail="Articolo non trovato")
            
        # Verifica che l'articolo non sia già nel kit
        existing_check = db.execute(text("""
            SELECT id FROM kit_articoli 
            WHERE kit_commerciale_id = :kit_id AND articolo_id = :articolo_id
        """), {"kit_id": kit_id, "articolo_id": articolo_data.articolo_id})
        
        if existing_check.fetchone():
            return {"success": False, "detail": "Articolo già presente nel kit"}
            
        # Inserisci l'articolo nel kit
        insert_query = text("""
            INSERT INTO kit_articoli (kit_commerciale_id, articolo_id, quantita, obbligatorio, ordine)
            VALUES (:kit_id, :articolo_id, :quantita, :obbligatorio, :ordine)
        """)
        
        db.execute(insert_query, {
            "kit_id": kit_id,
            "articolo_id": articolo_data.articolo_id,
            "quantita": articolo_data.quantita,
            "obbligatorio": articolo_data.obbligatorio,
            "ordine": articolo_data.ordine
        })
        db.commit()
        
        return {
            "success": True,
            "message": f"Articolo '{articolo.nome}' aggiunto al kit"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        return {"success": False, "detail": str(e)}

@router.delete("/{kit_id}/articoli/{articolo_kit_id}")
async def remove_articolo_from_kit(
    kit_id: int, 
    articolo_kit_id: int,
    db: Session = Depends(get_db)
):
    """Rimuovi articolo da kit commerciale"""
    try:
        # Verifica che l'articolo sia nel kit
        check_query = text("""
            SELECT ka.id, a.nome 
            FROM kit_articoli ka
            JOIN articoli a ON ka.articolo_id = a.id
            WHERE ka.id = :articolo_kit_id AND ka.kit_commerciale_id = :kit_id
        """)
        
        result = db.execute(check_query, {
            "articolo_kit_id": articolo_kit_id,
            "kit_id": kit_id
        })
        
        articolo_data = result.fetchone()
        if not articolo_data:
            raise HTTPException(status_code=404, detail="Articolo non trovato nel kit")
            
        # Rimuovi l'articolo dal kit
        delete_query = text("""
            DELETE FROM kit_articoli 
            WHERE id = :articolo_kit_id AND kit_commerciale_id = :kit_id
        """)
        
        db.execute(delete_query, {
            "articolo_kit_id": articolo_kit_id,
            "kit_id": kit_id
        })
        db.commit()
        
        return {
            "success": True,
            "message": f"Articolo '{articolo_data.nome}' rimosso dal kit"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        return {"success": False, "detail": str(e)}
