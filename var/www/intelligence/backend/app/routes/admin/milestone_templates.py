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

@router.get("/{template_id}/tasks")
async def get_milestone_template_tasks(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Recupera task associati a milestone template"""
    try:
        # Verifica che la milestone esista
        template_query = """
        SELECT id, nome FROM workflow_milestones wm 
        WHERE id = :template_id AND workflow_template_id IS NULL
        """
        template = db.execute(text(template_query), {"template_id": template_id}).fetchone()
        
        if not template:
            raise HTTPException(status_code=404, detail="Milestone template non trovato")
        
        # Recupera task associati
        tasks_query = """
        SELECT id, nome, descrizione, ordine, durata_stimata_ore as sla_hours,
               obbligatorio as is_required, tipo_task as priorita
        FROM milestone_task_templates
        WHERE milestone_id = :template_id
        ORDER BY ordine, nome
        """
        
        tasks_result = db.execute(text(tasks_query), {"template_id": template_id}).fetchall()
        
        tasks = []
        total_sla_hours = 0
        
        for task in tasks_result:
            task_data = {
                "id": task.id,
                "nome": task.nome,
                "descrizione": task.descrizione,
                "ordine": task.ordine,
                "sla_hours": task.sla_hours or 8,
                "is_required": task.is_required,
                "priorita": task.priorita or "standard"
            }
            tasks.append(task_data)
            total_sla_hours += task.sla_hours or 8
        
        # Calcola SLA milestone (arrotondato per eccesso)
        milestone_sla_giorni = max(1, (total_sla_hours + 7) // 8)
        
        return {
            "milestone": {"id": template.id, "nome": template.nome},
            "tasks": tasks,
            "milestone_sla_giorni": milestone_sla_giorni,
            "total_sla_hours": total_sla_hours
        }
        
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
