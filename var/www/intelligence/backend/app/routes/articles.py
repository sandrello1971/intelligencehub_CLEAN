from sqlalchemy import text
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
    search: str = "",
    tipo_prodotto: str = "",
    db: Session = Depends(get_db)
):
    """Lista articoli con responsabile"""
    try:
        base_query = """
        SELECT 
            a.id, a.codice, a.nome, a.descrizione, a.tipo_prodotto, 
            a.partner_id, a.prezzo_base, a.durata_mesi, a.attivo,
            a.tipologia_servizio_id, a.responsabile_user_id,
            a.modello_ticket_id,
            a.created_at, a.updated_at,
            u.username as responsabile_username, u.email as responsabile_email,
            CASE 
                WHEN u.first_name IS NOT NULL AND u.last_name IS NOT NULL 
                THEN u.first_name || ' ' || u.last_name
                WHEN u.name IS NOT NULL AND u.surname IS NOT NULL 
                THEN u.name || ' ' || u.surname
                ELSE u.username
            END as responsabile_display_name
        FROM articoli a
        LEFT JOIN users u ON a.responsabile_user_id = u.id
        WHERE a.attivo = true
        """
        
        params = {}
        
        if search:
            base_query += " AND (a.nome ILIKE :search OR a.codice ILIKE :search)"
            params["search"] = f"%{search}%"
        
        if tipo_prodotto:
            base_query += " AND a.tipo_prodotto = :tipo_prodotto"
            params["tipo_prodotto"] = tipo_prodotto
            
        base_query += " ORDER BY a.created_at DESC"
        
        result = db.execute(text(base_query), params)
        articles = []
        
        for row in result:
            articles.append({
                "id": row.id,
                "codice": row.codice,
                "nome": row.nome,
                "descrizione": row.descrizione,
                "tipo_prodotto": row.tipo_prodotto,
                "partner_id": row.partner_id,
                "prezzo_base": float(row.prezzo_base) if row.prezzo_base else None,
                "durata_mesi": row.durata_mesi,
                "attivo": row.attivo,
                "tipologia_servizio_id": row.tipologia_servizio_id,
                "responsabile_user_id": str(row.responsabile_user_id) if row.responsabile_user_id else None,
                "modello_ticket_id": str(row.modello_ticket_id) if row.modello_ticket_id else None,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "updated_at": row.updated_at.isoformat() if row.updated_at else None,
                # Info responsabile
                "responsabile_username": row.responsabile_username,
                "responsabile_email": row.responsabile_email,
                "responsabile_display_name": row.responsabile_display_name
            })
        
        return {
            "success": True,
            "count": len(articles),
            "articles": articles
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/users-disponibili")
async def get_users_disponibili(db: Session = Depends(get_db)):
    """Lista utenti per assegnazione responsabilità servizi"""
    try:
        query = text("""
        SELECT id, username, email, first_name, last_name, name, surname, role, is_active
        FROM users 
        WHERE is_active = true 
        ORDER BY 
            CASE 
                WHEN first_name IS NOT NULL AND last_name IS NOT NULL 
                THEN first_name || ' ' || last_name
                WHEN name IS NOT NULL AND surname IS NOT NULL 
                THEN name || ' ' || surname
                ELSE username
            END
        """)
        
        result = db.execute(query)
        users = []
        
        for row in result:
            # Determina il nome da mostrare
            display_name = None
            if row.first_name and row.last_name:
                display_name = f"{row.first_name} {row.last_name}"
            elif row.name and row.surname:
                display_name = f"{row.name} {row.surname}"
            else:
                display_name = row.username
                
            users.append({
                "id": str(row.id),
                "username": row.username,
                "email": row.email,
                "display_name": display_name,
                "role": row.role,
                "is_active": row.is_active
            })
        
        return {
            "success": True,
            "count": len(users),
            "users": users
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.put("/{article_id}")
async def update_article(article_id: int, article_data: dict, db: Session = Depends(get_db)):
    """Aggiorna articolo"""
    try:
        # Verifica che l'articolo esista
        check_query = text("SELECT id FROM articoli WHERE id = :article_id")
        if not db.execute(check_query, {"article_id": article_id}).first():
            raise HTTPException(status_code=404, detail="Articolo non trovato")
        
        # Prepara i campi per l'update
        update_fields = []
        params = {"article_id": article_id}
        
        if "codice" in article_data:
            update_fields.append("codice = :codice")
            params["codice"] = article_data["codice"]
            
        if "nome" in article_data:
            update_fields.append("nome = :nome")
            params["nome"] = article_data["nome"]
            
        if "descrizione" in article_data:
            update_fields.append("descrizione = :descrizione")
            params["descrizione"] = article_data["descrizione"]
            
        if "tipo_prodotto" in article_data:
            update_fields.append("tipo_prodotto = :tipo_prodotto")
            params["tipo_prodotto"] = article_data["tipo_prodotto"]
            
        if "tipologia_servizio_id" in article_data:
            if article_data["tipologia_servizio_id"]:
                update_fields.append("tipologia_servizio_id = :tipologia_servizio_id")
                params["tipologia_servizio_id"] = article_data["tipologia_servizio_id"]
            else:
                update_fields.append("tipologia_servizio_id = NULL")
                
        if "partner_id" in article_data:
            if article_data["partner_id"]:
                update_fields.append("partner_id = :partner_id")
                params["partner_id"] = article_data["partner_id"]
            else:
                update_fields.append("partner_id = NULL")
                
        if "responsabile_user_id" in article_data:
            if article_data["responsabile_user_id"]:
                update_fields.append("responsabile_user_id = :responsabile_user_id")
                params["responsabile_user_id"] = article_data["responsabile_user_id"]
            else:
                update_fields.append("responsabile_user_id = NULL")
                
        if "prezzo_base" in article_data:
            if article_data["prezzo_base"]:
                update_fields.append("prezzo_base = :prezzo_base")
                params["prezzo_base"] = article_data["prezzo_base"]
            else:
                update_fields.append("prezzo_base = NULL")
                
        if "durata_mesi" in article_data:
            if article_data["durata_mesi"]:
                update_fields.append("durata_mesi = :durata_mesi")
                params["durata_mesi"] = article_data["durata_mesi"]
            else:
                update_fields.append("durata_mesi = NULL")
                
        if "attivo" in article_data:
            update_fields.append("attivo = :attivo")
            params["attivo"] = article_data["attivo"]
        
        if "modello_ticket_id" in article_data:
            if article_data["modello_ticket_id"]:
                update_fields.append("modello_ticket_id = :modello_ticket_id")
                params["modello_ticket_id"] = article_data["modello_ticket_id"]
            else:
                update_fields.append("modello_ticket_id = NULL")
        
        if not update_fields:
            return {"success": False, "detail": "Nessun campo da aggiornare"}
        
        # Esegui l'update
        update_query = text(f"""
        UPDATE articoli 
        SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
        WHERE id = :article_id
        """)
        
        db.execute(update_query, params)
        db.commit()
        
        return {
            "success": True,
            "message": f"Articolo aggiornato con successo"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        return {"success": False, "detail": str(e)}
@router.delete("/{article_id}")
async def delete_article(
    article_id: int,
    db: Session = Depends(get_db)
):
    """
    Disattiva articolo (soft delete)
    """
    try:
        articolo = db.query(Articolo).filter(Articolo.id == article_id).first()
        
        if not articolo:
            raise HTTPException(status_code=404, detail="Articolo non trovato")
        
        articolo.attivo = False
        db.commit()
        
        return {
            "success": True,
            "message": f"Articolo {articolo.codice} disattivato con successo"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ Errore delete_article: {e}")
        raise HTTPException(status_code=500, detail=f"Errore eliminazione: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check per le routes articoli"""
    return {"status": "healthy", "service": "articles", "version": "1.0"}
