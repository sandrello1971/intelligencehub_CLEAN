"""
Intelligence AI Platform - Articles Routes  
API endpoints per gestione articoli
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.articles import Articolo

router = APIRouter(prefix="/articles", tags=["Articles Management"])

@router.get("/health")
async def health_check():
    """Health check per le routes articoli"""
    return {"status": "healthy", "service": "articles", "version": "1.0"}

@router.get("/")
async def get_articles(
    search: Optional[str] = Query(None, description="Cerca per codice o nome"),
    tipo_prodotto: Optional[str] = Query(None, description="Filtra per tipo: semplice o composito"),
    attivo: Optional[bool] = Query(True, description="Filtra per articoli attivi"),
    db: Session = Depends(get_db)
):
    """Lista tutti gli articoli con filtri opzionali"""
    try:
        query = db.query(Articolo)
        
        if attivo is not None:
            query = query.filter(Articolo.attivo == attivo)
            
        if tipo_prodotto:
            query = query.filter(Articolo.tipo_prodotto == tipo_prodotto)
            
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                (Articolo.codice.ilike(search_filter)) |
                (Articolo.nome.ilike(search_filter))
            )
        
        articoli = query.order_by(Articolo.codice).all()
        
        return {
            "success": True,
            "count": len(articoli),
            "articles": [articolo.to_dict() for articolo in articoli]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore interno: {str(e)}")

@router.post("/")
async def create_article(article_data: dict, db: Session = Depends(get_db)):
    """Crea nuovo articolo"""
    try:
        existing = db.query(Articolo).filter(Articolo.codice == article_data.get('codice')).first()
        if existing:
            raise HTTPException(status_code=400, detail="Codice articolo già esistente")
        
        if article_data.get('tipo_prodotto') not in ['semplice', 'composito']:
            raise HTTPException(status_code=400, detail="tipo_prodotto deve essere 'semplice' o 'composito'")
        
        nuovo_articolo = Articolo(
            codice=article_data.get('codice'),
            nome=article_data.get('nome'),
            descrizione=article_data.get('descrizione'),
            tipo_prodotto=article_data.get('tipo_prodotto'),
            attivo=article_data.get('attivo', True)
        )
        
        db.add(nuovo_articolo)
        db.commit()
        db.refresh(nuovo_articolo)
        
        # Se è composito, crea automaticamente un kit commerciale
        kit_created = False
        if nuovo_articolo.tipo_prodotto == 'composito':
            try:
                # Importa qui per evitare circular imports
                from sqlalchemy import text
                
                # Crea kit commerciale con SQL diretto
                db.execute(text("""
                    INSERT INTO kit_commerciali (nome, descrizione, articolo_principale_id, attivo, created_at)
                    VALUES (:nome, :descrizione, :articolo_id, true, CURRENT_TIMESTAMP)
                """), {
                    'nome': f"Kit {nuovo_articolo.nome}",
                    'descrizione': f"Kit commerciale per {nuovo_articolo.nome}",
                    'articolo_id': nuovo_articolo.id
                })
                db.commit()
                kit_created = True
            except Exception as kit_error:
                print(f"⚠️ Errore creazione kit: {kit_error}")
        
        result_message = f"Articolo {nuovo_articolo.codice} creato con successo"
        if kit_created:
            result_message += f" + Kit commerciale creato automaticamente"
        
        return {
            "success": True,
            "message": result_message,
            "article": nuovo_articolo.to_dict(),
            "kit_created": kit_created
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore creazione: {str(e)}")

@router.put("/{article_id}")
async def update_article(article_id: int, article_data: dict, db: Session = Depends(get_db)):
    """Aggiorna articolo esistente"""
    try:
        articolo = db.query(Articolo).filter(Articolo.id == article_id).first()
        if not articolo:
            raise HTTPException(status_code=404, detail="Articolo non trovato")
        
        # Aggiorna solo i campi forniti
        for field, value in article_data.items():
            if hasattr(articolo, field) and value is not None:
                setattr(articolo, field, value)
        
        db.commit()
        db.refresh(articolo)
        
        return {
            "success": True,
            "message": f"Articolo {articolo.codice} aggiornato con successo",
            "article": articolo.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore aggiornamento: {str(e)}")

@router.delete("/{article_id}")
async def delete_article(article_id: int, db: Session = Depends(get_db)):
    """CANCELLA DEFINITIVAMENTE articolo"""
    try:
        articolo = db.query(Articolo).filter(Articolo.id == article_id).first()
        if not articolo:
            raise HTTPException(status_code=404, detail="Articolo non trovato")
        
        articolo_info = f"{articolo.codice} - {articolo.nome}"
        
        # Cancellazione definitiva
        db.delete(articolo)
        db.commit()
        
        return {
            "success": True,
            "message": f"Articolo {articolo_info} cancellato definitivamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore cancellazione: {str(e)}")

@router.get("/{article_id}")
async def get_article(article_id: int, db: Session = Depends(get_db)):
    """Ottieni singolo articolo per ID"""
    try:
        articolo = db.query(Articolo).filter(Articolo.id == article_id).first()
        if not articolo:
            raise HTTPException(status_code=404, detail="Articolo non trovato")
        return {"success": True, "article": articolo.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore interno: {str(e)}")
