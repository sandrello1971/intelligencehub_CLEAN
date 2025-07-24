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
               tipo_milestone as categoria, sla_giorni, created_at,
               (SELECT COUNT(*) FROM milestone_task_templates WHERE milestone_id = wm.id) as task_count, 0 as usage_count
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
    milestone_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    try:
        max_order = db.execute(text("SELECT COALESCE(MAX(ordine), 0) FROM workflow_milestones wm WHERE workflow_template_id IS NULL")).scalar()
        
        query = """
        INSERT INTO workflow_milestones 
        (nome, descrizione, ordine, durata_stimata_giorni, sla_giorni, tipo_milestone)
        VALUES (:nome, :descrizione, :ordine, :durata_giorni, :sla_giorni, :categoria)
        RETURNING id, nome, descrizione, durata_stimata_giorni, sla_giorni, tipo_milestone as categoria, created_at
        """
        
        result = db.execute(text(query), {
            "nome": milestone_data["nome"],
            "descrizione": milestone_data.get("descrizione"),
            "ordine": max_order + 1,
            "durata_giorni": milestone_data.get("durata_stimata_giorni"),
            "sla_giorni": milestone_data.get("sla_giorni", 5),
            "categoria": milestone_data.get("categoria", "standard")
        }).fetchone()
        
        db.commit()
        return {"id": result.id, "nome": result.nome, "message": "Creato"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore: {str(e)}")

@router.delete("/{template_id}")
async def delete_milestone_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    try:
        result = db.execute(text("DELETE FROM workflow_milestones wm WHERE id = :id AND workflow_template_id IS NULL"), {"id": template_id})
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Template non trovato")
        db.commit()
        return {"message": "Template eliminato"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore: {str(e)}")

@router.get("/{template_id}/tasks")
async def get_milestone_template_tasks(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Recupera task associati a milestone template"""
    try:
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
        milestone_check = db.execute(text("SELECT id FROM workflow_milestones wm WHERE id = :id AND workflow_template_id IS NULL"), {"id": template_id}).fetchone()
        if not milestone_check:
            raise HTTPException(status_code=404, detail="Milestone non trovata")
        
        query = """
        INSERT INTO milestone_task_templates 
        (milestone_id, nome, descrizione, ordine, durata_stimata_ore, obbligatorio, tipo_task)
        SELECT :milestone_id, tsk_code, tsk_description, :ordine, sla_giorni * 8, true, tsk_category
        FROM tasks_global 
        WHERE id = :task_id
        """
        
        db.execute(text(query), {
            "milestone_id": template_id,
            "task_id": task_id,
            "ordine": assignment_data.get("ordine", 1)
        })
        
        db.commit()
        return {"message": "Task associato alla milestone"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore: {str(e)}")
