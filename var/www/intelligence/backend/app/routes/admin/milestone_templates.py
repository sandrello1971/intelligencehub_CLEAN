# routes/admin/milestone_templates.py
# API Routes per Milestone Templates Riutilizzabili - IntelligenceHUB

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.routes.auth import get_current_user_dep
from app.models.users import User

router = APIRouter(prefix="/api/v1/admin/milestone-templates", tags=["Milestone Templates"])

@router.post("/")
async def create_milestone_template(
    milestone_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Crea milestone template riutilizzabile"""
    try:
        query = """
        INSERT INTO milestone_templates_library 
        (nome, descrizione, durata_stimata_giorni, categoria, sla_giorni, created_by)
        VALUES 
        (:nome, :descrizione, :durata_giorni, :categoria, :sla_giorni, :created_by)
        RETURNING id, nome, descrizione, durata_stimata_giorni, categoria, sla_giorni, created_at
        """
        
        result = db.execute(text(query), {
            "nome": milestone_data["nome"],
            "descrizione": milestone_data.get("descrizione"),
            "durata_giorni": milestone_data.get("durata_stimata_giorni"),
            "categoria": milestone_data.get("categoria", "standard"),
            "sla_giorni": milestone_data.get("sla_giorni"),
            "created_by": current_user.id
        }).fetchone()
        
        db.commit()
        
        return {
            "id": result.id,
            "nome": result.nome,
            "descrizione": result.descrizione,
            "durata_stimata_giorni": result.durata_stimata_giorni,
            "categoria": result.categoria,
            "sla_giorni": result.sla_giorni,
            "created_at": result.created_at,
            "task_templates": []
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore creazione milestone template: {str(e)}")

@router.get("/")
async def list_milestone_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Lista milestone templates"""
    try:
        query = """
        SELECT mtl.id, mtl.nome, mtl.descrizione, mtl.durata_stimata_giorni, 
               mtl.categoria, mtl.sla_giorni, mtl.created_at,
               COUNT(mtt.task_template_id) as task_count
        FROM milestone_templates_library mtl
        LEFT JOIN milestone_template_tasks mtt ON mtl.id = mtt.milestone_template_id
        GROUP BY mtl.id, mtl.nome, mtl.descrizione, mtl.durata_stimata_giorni, 
                 mtl.categoria, mtl.sla_giorni, mtl.created_at
        ORDER BY mtl.nome
        """
        
        result = db.execute(text(query)).fetchall()
        
        templates = []
        for row in result:
            templates.append({
                "id": row.id,
                "nome": row.nome,
                "descrizione": row.descrizione,
                "durata_stimata_giorni": row.durata_stimata_giorni,
                "categoria": row.categoria,
                "sla_giorni": row.sla_giorni,
                "created_at": row.created_at,
                "task_count": row.task_count,
                "usage_count": 0  # TODO: calcolare da workflow che usano questa milestone
            })
        
        return templates
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore recupero milestone templates: {str(e)}")

@router.delete("/{template_id}")
async def delete_milestone_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Elimina milestone template"""
    try:
        # Elimina milestone template (le associazioni task vengono eliminate in cascade)
        query = "DELETE FROM milestone_templates_library WHERE id = :template_id"
        result = db.execute(text(query), {"template_id": template_id})
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Milestone template non trovato")
        
        db.commit()
        return {"message": "Milestone template eliminato"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore eliminazione: {str(e)}")

@router.get("/{template_id}/tasks")
async def get_milestone_template_tasks(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Recupera task associati a milestone template"""
    try:
        query = """
        SELECT mt.id, mt.nome, mt.descrizione, mt.sla_hours, mt.priorita,
               mtt.ordine, mtt.is_required
        FROM modelli_task mt
        JOIN milestone_template_tasks mtt ON mt.id = mtt.task_template_id
        WHERE mtt.milestone_template_id = :template_id
        ORDER BY mtt.ordine
        """
        
        result = db.execute(text(query), {"template_id": template_id}).fetchall()
        
        tasks = []
        for row in result:
            tasks.append({
                "id": row.id,
                "nome": row.nome,
                "descrizione": row.descrizione,
                "ordine": row.ordine,
                "sla_hours": row.sla_hours,
                "priorita": row.priorita,
                "is_required": row.is_required
            })
        
        return tasks
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore recupero task: {str(e)}")

@router.post("/{template_id}/tasks/{task_id}")
async def assign_task_to_milestone_template(
    template_id: int,
    task_id: UUID,
    assignment_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Assegna task a milestone template"""
    try:
        # Verifica che milestone template esista
        milestone_check = db.execute(
            text("SELECT id FROM milestone_templates_library WHERE id = :id"),
            {"id": template_id}
        ).fetchone()
        
        if not milestone_check:
            raise HTTPException(status_code=404, detail="Milestone template non trovato")
        
        # Verifica che task template esista
        task_check = db.execute(
            text("SELECT id FROM modelli_task WHERE id = :id"),
            {"id": task_id}
        ).fetchone()
        
        if not task_check:
            raise HTTPException(status_code=404, detail="Task template non trovato")
        
        # Inserisci associazione
        query = """
        INSERT INTO milestone_template_tasks 
        (milestone_template_id, task_template_id, ordine, is_required)
        VALUES (:milestone_id, :task_id, :ordine, :is_required)
        ON CONFLICT (milestone_template_id, task_template_id) 
        DO UPDATE SET ordine = :ordine, is_required = :is_required
        """
        
        db.execute(text(query), {
            "milestone_id": template_id,
            "task_id": task_id,
            "ordine": assignment_data.get("ordine", 1),
            "is_required": assignment_data.get("is_required", True)
        })
        
        db.commit()
        
        return {"message": "Task assegnato alla milestone template"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore assegnazione task: {str(e)}")

@router.delete("/{template_id}/tasks/{task_id}")
async def remove_task_from_milestone_template(
    template_id: int,
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Rimuove task da milestone template"""
    try:
        query = """
        DELETE FROM milestone_template_tasks 
        WHERE milestone_template_id = :milestone_id AND task_template_id = :task_id
        """
        
        result = db.execute(text(query), {
            "milestone_id": template_id,
            "task_id": task_id
        })
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Associazione non trovata")
        
        db.commit()
        
        return {"message": "Task rimosso dalla milestone template"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore rimozione task: {str(e)}")

@router.put("/{template_id}")
async def update_milestone_template(
    template_id: int,
    milestone_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Aggiorna milestone template esistente"""
    try:
        # Verifica che il template esista
        check_query = "SELECT id FROM milestone_templates_library WHERE id = :template_id"
        existing = db.execute(text(check_query), {"template_id": template_id}).fetchone()
        
        if not existing:
            raise HTTPException(status_code=404, detail="Milestone template non trovato")
        
        # Aggiorna il template
        update_query = """
        UPDATE milestone_templates_library 
        SET nome = :nome, 
            descrizione = :descrizione, 
            durata_stimata_giorni = :durata_giorni,
            categoria = :categoria,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = :template_id
        RETURNING id, nome, descrizione, durata_stimata_giorni, categoria, sla_giorni, created_at
        """
        
        result = db.execute(text(update_query), {
            "template_id": template_id,
            "nome": milestone_data["nome"],
            "descrizione": milestone_data.get("descrizione"),
            "durata_giorni": milestone_data.get("durata_stimata_giorni"),
            "categoria": milestone_data.get("categoria", "standard")
        }).fetchone()
        
        db.commit()
        
        return {
            "id": result.id,
            "nome": result.nome,
            "descrizione": result.descrizione,
            "durata_stimata_giorni": result.durata_stimata_giorni,
            "categoria": result.categoria,
            "sla_giorni": result.sla_giorni,
            "created_at": result.created_at
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore aggiornamento milestone template: {str(e)}")

@router.put("/{template_id}")
async def update_milestone_template(
    template_id: int,
    milestone_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Aggiorna milestone template esistente"""
    try:
        check_query = "SELECT id FROM milestone_templates_library WHERE id = :template_id"
        existing = db.execute(text(check_query), {"template_id": template_id}).fetchone()
        
        if not existing:
            raise HTTPException(status_code=404, detail="Milestone template non trovato")
        
        update_query = """
        UPDATE milestone_templates_library 
        SET nome = :nome, 
            descrizione = :descrizione, 
            durata_stimata_giorni = :durata_giorni,
            categoria = :categoria,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = :template_id
        RETURNING id, nome, descrizione, durata_stimata_giorni, categoria, sla_giorni, created_at
        """
        
        result = db.execute(text(update_query), {
            "template_id": template_id,
            "nome": milestone_data["nome"],
            "descrizione": milestone_data.get("descrizione"),
            "durata_giorni": milestone_data.get("durata_stimata_giorni"),
            "categoria": milestone_data.get("categoria", "standard")
        }).fetchone()
        
        db.commit()
        
        return {
            "id": result.id,
            "nome": result.nome,
            "descrizione": result.descrizione,
            "durata_stimata_giorni": result.durata_stimata_giorni,
            "categoria": result.categoria,
            "sla_giorni": result.sla_giorni,
            "created_at": result.created_at
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore aggiornamento milestone template: {str(e)}")

@router.put("/{template_id}")
async def update_milestone_template(
    template_id: int,
    milestone_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Aggiorna milestone template esistente"""
    try:
        check_query = "SELECT id FROM milestone_templates_library WHERE id = :template_id"
        existing = db.execute(text(check_query), {"template_id": template_id}).fetchone()
        
        if not existing:
            raise HTTPException(status_code=404, detail="Milestone template non trovato")
        
        update_query = """
        UPDATE milestone_templates_library 
        SET nome = :nome, 
            descrizione = :descrizione, 
            durata_stimata_giorni = :durata_giorni,
            categoria = :categoria,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = :template_id
        RETURNING id, nome, descrizione, durata_stimata_giorni, categoria, sla_giorni, created_at
        """
        
        result = db.execute(text(update_query), {
            "template_id": template_id,
            "nome": milestone_data["nome"],
            "descrizione": milestone_data.get("descrizione"),
            "durata_giorni": milestone_data.get("durata_stimata_giorni"),
            "categoria": milestone_data.get("categoria", "standard")
        }).fetchone()
        
        db.commit()
        
        return {
            "id": result.id,
            "nome": result.nome,
            "descrizione": result.descrizione,
            "durata_stimata_giorni": result.durata_stimata_giorni,
            "categoria": result.categoria,
            "sla_giorni": result.sla_giorni,
            "created_at": result.created_at
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore aggiornamento milestone template: {str(e)}")
