
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.routes.auth import get_current_user_dep
from app.models.users import User

router = APIRouter(prefix="/api/v1/admin/milestone-templates", tags=["Milestone Templates"])

@router.get("/")
async def list_milestone_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    try:
        query = """
        SELECT id, nome, descrizione, durata_stimata_giorni, 
               tipo_milestone as categoria, 
               (SELECT COALESCE(CEILING(SUM(durata_stimata_ore::numeric) / 8), sla_giorni) 
                FROM milestone_task_templates WHERE milestone_id = wm.id) as sla_giorni, 
               created_at,
               (SELECT COUNT(*) FROM milestone_task_templates WHERE milestone_id = wm.id) as task_count, 
               0 as usage_count
        FROM workflow_milestones wm 
        WHERE workflow_template_id IS NULL
        ORDER BY ordine, nome
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
                "usage_count": row.usage_count
            })
        
        return templates
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore: {str(e)}")

@router.post("/")
async def create_milestone_template(
    template_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Crea nuovo milestone template"""
    try:
        # Valori di default
        nome = template_data.get("nome", "")
        descrizione = template_data.get("descrizione", "")
        durata_stimata_giorni = template_data.get("durata_stimata_giorni")
        sla_giorni = template_data.get("sla_giorni", 7)
        warning_giorni = template_data.get("warning_giorni", 2)
        escalation_giorni = template_data.get("escalation_giorni", 1)
        tipo_milestone = template_data.get("tipo_milestone", "standard")
        auto_generate_tickets = template_data.get("auto_generate_tickets", False)
        ordine = template_data.get("ordine", 1)
        
        if not nome.strip():
            raise HTTPException(status_code=400, detail="Nome template obbligatorio")
        
        query = """
        INSERT INTO workflow_milestones 
        (nome, descrizione, durata_stimata_giorni, sla_giorni, warning_giorni, 
         escalation_giorni, tipo_milestone, auto_generate_tickets, ordine, workflow_template_id)
        VALUES 
        (:nome, :descrizione, :durata_stimata_giorni, :sla_giorni, :warning_giorni,
         :escalation_giorni, :tipo_milestone, :auto_generate_tickets, :ordine, NULL)
        RETURNING id, created_at
        """
        
        result = db.execute(text(query), {
            "nome": nome,
            "descrizione": descrizione,
            "durata_stimata_giorni": durata_stimata_giorni,
            "sla_giorni": sla_giorni,
            "warning_giorni": warning_giorni,
            "escalation_giorni": escalation_giorni,
            "tipo_milestone": tipo_milestone,
            "auto_generate_tickets": auto_generate_tickets,
            "ordine": ordine
        }).fetchone()
        
        db.commit()
        
        return {
            "id": result.id,
            "nome": nome,
            "descrizione": descrizione,
            "durata_stimata_giorni": durata_stimata_giorni,
            "sla_giorni": sla_giorni,
            "warning_giorni": warning_giorni,
            "escalation_giorni": escalation_giorni,
            "tipo_milestone": tipo_milestone,
            "auto_generate_tickets": auto_generate_tickets,
            "ordine": ordine,
            "created_at": result.created_at
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore creazione template: {str(e)}")

 	
# Aggiungi questo endpoint dopo il POST "/" nel file milestone_templates.py

@router.put("/{template_id}")
async def update_milestone_template(
    template_id: int,
    template_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Modifica milestone template esistente"""
    try:
        # Verifica che il template esista
        check_query = """
        SELECT id FROM workflow_milestones 
        WHERE id = :template_id AND workflow_template_id IS NULL
        """
        existing = db.execute(text(check_query), {"template_id": template_id}).fetchone()
        
        if not existing:
            raise HTTPException(status_code=404, detail="Milestone template non trovato")
        
        # Valori di update
        nome = template_data.get("nome", "")
        descrizione = template_data.get("descrizione", "")
        durata_stimata_giorni = template_data.get("durata_stimata_giorni")
        sla_giorni = template_data.get("sla_giorni", 7)
        warning_giorni = template_data.get("warning_giorni", 2)
        escalation_giorni = template_data.get("escalation_giorni", 1)
        tipo_milestone = template_data.get("tipo_milestone", "standard")
        auto_generate_tickets = template_data.get("auto_generate_tickets", False)
        ordine = template_data.get("ordine", 1)
        
        if not nome.strip():
            raise HTTPException(status_code=400, detail="Nome template obbligatorio")
        
        # Aggiorna il template
        update_query = """
        UPDATE workflow_milestones SET
            nome = :nome,
            descrizione = :descrizione,
            durata_stimata_giorni = :durata_stimata_giorni,
            sla_giorni = :sla_giorni,
            warning_giorni = :warning_giorni,
            escalation_giorni = :escalation_giorni,
            tipo_milestone = :tipo_milestone,
            auto_generate_tickets = :auto_generate_tickets,
            ordine = :ordine
        WHERE id = :template_id AND workflow_template_id IS NULL
        RETURNING id, created_at
        """
        
        result = db.execute(text(update_query), {
            "template_id": template_id,
            "nome": nome,
            "descrizione": descrizione,
            "durata_stimata_giorni": durata_stimata_giorni,
            "sla_giorni": sla_giorni,
            "warning_giorni": warning_giorni,
            "escalation_giorni": escalation_giorni,
            "tipo_milestone": tipo_milestone,
            "auto_generate_tickets": auto_generate_tickets,
            "ordine": ordine
        }).fetchone()
        
        db.commit()
        
        return {
            "id": template_id,
            "nome": nome,
            "descrizione": descrizione,
            "durata_stimata_giorni": durata_stimata_giorni,
            "sla_giorni": sla_giorni,
            "warning_giorni": warning_giorni,
            "escalation_giorni": escalation_giorni,
            "tipo_milestone": tipo_milestone,
            "auto_generate_tickets": auto_generate_tickets,
            "ordine": ordine,
            "created_at": result.created_at,
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore aggiornamento template: {str(e)}")



    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore: {str(e)}")

@router.post("/{template_id}/tasks/{task_id}")
async def assign_task_to_milestone(
    template_id: int,
    task_id: int,
    assignment_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Associa task esistente alla milestone"""
    try:
        # Verifica che la milestone esista
        milestone_check = db.execute(text("SELECT id FROM workflow_milestones wm WHERE id = :id AND workflow_template_id IS NULL"), {"id": template_id}).fetchone()
        if not milestone_check:
            raise HTTPException(status_code=404, detail="Milestone non trovata")
        
        # Verifica che il task esista
        task_check = db.execute(text("SELECT id, tsk_code, tsk_description, sla_giorni FROM tasks_global WHERE id = :id"), {"id": task_id}).fetchone()
        if not task_check:
            raise HTTPException(status_code=404, detail="Task non trovato")
        
        # Verifica che il task non sia già associato
        existing_check = db.execute(text("SELECT id FROM milestone_task_templates WHERE milestone_id = :milestone_id AND nome = :task_name"), 
                                  {"milestone_id": template_id, "task_name": task_check.tsk_code}).fetchone()
        if existing_check:
            raise HTTPException(status_code=400, detail="Task già associato alla milestone")
        
        # Associa il task
        query = """
        INSERT INTO milestone_task_templates 
        (milestone_id, nome, descrizione, ordine, durata_stimata_ore, obbligatorio, tipo_task)
        VALUES (:milestone_id, :nome, :descrizione, :ordine, :durata_ore, true, 'standard')
        """
        
        db.execute(text(query), {
            "milestone_id": template_id,
            "nome": task_check.tsk_code,
            "descrizione": task_check.tsk_description,
            "ordine": assignment_data.get("ordine", 1),
            "durata_ore": task_check.sla_giorni * 8  # Converti giorni in ore
        })
        
        db.commit()
        return {"message": "Task associato alla milestone con successo", "task_name": task_check.tsk_code}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore: {str(e)}")

@router.delete("/{template_id}/tasks/{task_template_id}")
async def remove_task_from_milestone(
    template_id: int,
    task_template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Rimuove task dalla milestone"""
    try:
        # Verifica ed elimina
        result = db.execute(text("DELETE FROM milestone_task_templates WHERE id = :id AND milestone_id = :milestone_id"), 
                          {"id": task_template_id, "milestone_id": template_id})
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Task non trovato nella milestone")
        
        db.commit()
        return {"message": "Task rimosso dalla milestone con successo"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore: {str(e)}")

@router.put("/{template_id}/tasks/reorder")
async def reorder_milestone_tasks(
    template_id: int,
    request: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Aggiorna ordine task milestone"""
    try:
        tasks_order = request.get("tasks_order", [])
        updated_count = 0
        
        for task_data in tasks_order:
            task_id = task_data.get("id")
            nuovo_ordine = task_data.get("ordine")
            
            if task_id and nuovo_ordine is not None:
                result = db.execute(text("""
                    UPDATE milestone_task_templates 
                    SET ordine = :ordine 
                    WHERE id = :task_id AND milestone_id = :milestone_id
                """), {
                    "ordine": nuovo_ordine,
                    "task_id": task_id,
                    "milestone_id": template_id
                })
                updated_count += result.rowcount
        
        db.commit()
        return {"message": f"Aggiornati {updated_count} task", "updated_tasks": updated_count}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore: {str(e)}")

@router.post("/{template_id}/create-task")
async def create_milestone_task(
    template_id: int,
    task_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Crea nuovo task per la milestone"""
    try:
        # Verifica che la milestone esista
        milestone_check = db.execute(text("SELECT id FROM workflow_milestones WHERE id = :id"), 
                                   {"id": template_id}).fetchone()
        if not milestone_check:
            raise HTTPException(status_code=404, detail="Milestone non trovata")
        
        # Calcola il prossimo ordine
        max_order_result = db.execute(text("""
            SELECT COALESCE(MAX(ordine), 0) as max_ordine
            FROM milestone_task_templates 
            WHERE milestone_id = :milestone_id
        """), {"milestone_id": template_id}).fetchone()
        
        next_order = (max_order_result.max_ordine or 0) + 1
        
        # Inserisce il nuovo task
        query = """
        INSERT INTO milestone_task_templates 
        (milestone_id, nome, descrizione, ordine, durata_stimata_ore, 
         ruolo_responsabile, obbligatorio, tipo_task)
        VALUES 
        (:milestone_id, :nome, :descrizione, :ordine, :durata_stimata_ore,
         :ruolo_responsabile, :obbligatorio, :tipo_task)
        RETURNING id
        """
        
        result = db.execute(text(query), {
            "milestone_id": template_id,
            "nome": task_data.get("nome", "Nuovo Task"),
            "descrizione": task_data.get("descrizione", ""),
            "ordine": next_order,
            "durata_stimata_ore": task_data.get("durata_stimata_ore", 8),
            "ruolo_responsabile": task_data.get("ruolo_responsabile", ""),
            "obbligatorio": task_data.get("obbligatorio", True),
            "tipo_task": task_data.get("tipo_task", "standard")
        }).fetchone()
        
        db.commit()
        
        return {
            "message": "Task creato con successo",
            "task_id": result.id,
            "ordine": next_order
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore: {str(e)}")

@router.get("/{template_id}/tasks")
async def get_milestone_tasks(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Recupera task della milestone ordinati per ordine"""
    try:
        # Verifica che la milestone esista
        milestone_check = db.execute(text("SELECT id FROM workflow_milestones WHERE id = :id AND workflow_template_id IS NULL"), 
                                   {"id": template_id}).fetchone()
        if not milestone_check:
            raise HTTPException(status_code=404, detail="Milestone template non trovata")
        
        query = """
        SELECT id, milestone_id, nome, descrizione, ordine, durata_stimata_ore,
               ruolo_responsabile, obbligatorio, tipo_task, created_at
        FROM milestone_task_templates
        WHERE milestone_id = :milestone_id
        ORDER BY ordine, nome
        """
        
        result = db.execute(text(query), {"milestone_id": template_id}).fetchall()
        
        tasks = []
        for row in result:
            tasks.append({
                "id": row.id,
                "milestone_id": row.milestone_id,
                "nome": row.nome,
                "descrizione": row.descrizione or "",
                "ordine": row.ordine,
                "sla_hours": row.durata_stimata_ore or 0,
                "ruolo_responsabile": row.ruolo_responsabile or "",
                "is_required": row.obbligatorio,
                "priorita": row.tipo_task,
                "created_at": str(row.created_at)
            })
        
        total_hours = sum(task["sla_hours"] for task in tasks)
        milestone_sla_giorni = max(1, (total_hours + 7) // 8)
        
        return {
            "tasks": tasks,
            "milestone_sla_giorni": milestone_sla_giorni,
            "total_hours": total_hours
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore: {str(e)}")
