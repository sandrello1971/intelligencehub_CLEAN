# routes/admin/workflow_management.py
# API Routes per Gestione Avanzata Workflow - IntelligenceHUB

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from app.core.database import get_db
from app.routes.auth import get_current_user_dep
from app.models.users import User

router = APIRouter(prefix="/api/v1/admin/workflow-management", tags=["Workflow Management"])

# ===== UTILITY SCHEMAS =====

class WorkflowCloneRequest(BaseModel):
    """Schema per clonare workflow"""
    source_workflow_id: int
    new_name: str
    new_articolo_id: Optional[int] = None
    clone_milestones: bool = True
    clone_tasks: bool = True

class MilestoneReorderRequest(BaseModel):
    """Schema per riordinare milestone"""
    milestone_orders: List[Dict[str, int]]  # [{"milestone_id": 1, "ordine": 1}, ...]

class WorkflowValidationResponse(BaseModel):
    """Schema per validazione workflow"""
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    statistics: Dict[str, Any] = {}

# ===== WORKFLOW OPERATIONS =====

@router.post("/workflows/{workflow_id}/clone")
async def clone_workflow(
    workflow_id: int,
    clone_request: WorkflowCloneRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Clona un workflow esistente"""
    try:
        # Verifica che il workflow sorgente esista
        source_query = """
        SELECT * FROM workflow_templates WHERE id = :workflow_id
        """
        source = db.execute(text(source_query), {"workflow_id": workflow_id}).fetchone()
        
        if not source:
            raise HTTPException(status_code=404, detail="Workflow sorgente non trovato")
        
        # Crea nuovo workflow
        create_workflow_query = """
        INSERT INTO workflow_templates 
        (nome, descrizione, articolo_id, durata_stimata_giorni, ordine, wkf_code, wkf_description, attivo)
        VALUES 
        (:nome, :descrizione, :articolo_id, :durata_stimata_giorni, :ordine, :wkf_code, :wkf_description, :attivo)
        RETURNING id
        """
        
        new_workflow = db.execute(text(create_workflow_query), {
            "nome": clone_request.new_name,
            "descrizione": f"Clonato da: {source.nome}",
            "articolo_id": clone_request.new_articolo_id or source.articolo_id,
            "durata_stimata_giorni": source.durata_stimata_giorni,
            "ordine": source.ordine,
            "wkf_code": f"{source.wkf_code}_CLONE" if source.wkf_code else None,
            "wkf_description": source.wkf_description,
            "attivo": source.attivo
        }).fetchone()
        
        new_workflow_id = new_workflow.id
        
        # Clona milestone se richiesto
        if clone_request.clone_milestones:
            milestones_query = """
            SELECT * FROM workflow_milestones 
            WHERE workflow_template_id = :source_id 
            ORDER BY ordine
            """
            milestones = db.execute(text(milestones_query), {"source_id": workflow_id}).fetchall()
            
            milestone_mapping = {}  # Per mappare vecchi ID con nuovi ID
            
            for milestone in milestones:
                create_milestone_query = """
                INSERT INTO workflow_milestones 
                (workflow_template_id, nome, descrizione, ordine, durata_stimata_giorni,
                 sla_giorni, warning_giorni, escalation_giorni, tipo_milestone, auto_generate_tickets)
                VALUES 
                (:workflow_template_id, :nome, :descrizione, :ordine, :durata_stimata_giorni,
                 :sla_giorni, :warning_giorni, :escalation_giorni, :tipo_milestone, :auto_generate_tickets)
                RETURNING id
                """
                
                new_milestone = db.execute(text(create_milestone_query), {
                    "workflow_template_id": new_workflow_id,
                    "nome": milestone.nome,
                    "descrizione": milestone.descrizione,
                    "ordine": milestone.ordine,
                    "durata_stimata_giorni": milestone.durata_stimata_giorni,
                    "sla_giorni": milestone.sla_giorni,
                    "warning_giorni": milestone.warning_giorni,
                    "escalation_giorni": milestone.escalation_giorni,
                    "tipo_milestone": milestone.tipo_milestone,
                    "auto_generate_tickets": milestone.auto_generate_tickets
                }).fetchone()
                
                milestone_mapping[milestone.id] = new_milestone.id
                
                # Clona task se richiesto
                if clone_request.clone_tasks:
                    tasks_query = """
                    SELECT * FROM milestone_task_templates 
                    WHERE milestone_id = :milestone_id 
                    ORDER BY ordine
                    """
                    tasks = db.execute(text(tasks_query), {"milestone_id": milestone.id}).fetchall()
                    
                    for task in tasks:
                        create_task_query = """
                        INSERT INTO milestone_task_templates 
                        (milestone_id, nome, descrizione, ordine, durata_stimata_ore,
                         ruolo_responsabile, obbligatorio, tipo_task, checklist_template)
                        VALUES 
                        (:milestone_id, :nome, :descrizione, :ordine, :durata_stimata_ore,
                         :ruolo_responsabile, :obbligatorio, :tipo_task, :checklist_template)
                        """
                        
                        db.execute(text(create_task_query), {
                            "milestone_id": new_milestone.id,
                            "nome": task.nome,
                            "descrizione": task.descrizione,
                            "ordine": task.ordine,
                            "durata_stimata_ore": task.durata_stimata_ore,
                            "ruolo_responsabile": task.ruolo_responsabile,
                            "obbligatorio": task.obbligatorio,
                            "tipo_task": task.tipo_task,
                            "checklist_template": task.checklist_template
                        })
        
        db.commit()
        
        return {
            "message": "Workflow clonato con successo",
            "new_workflow_id": new_workflow_id,
            "milestones_cloned": len(milestone_mapping) if clone_request.clone_milestones else 0
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore clonazione workflow: {str(e)}")

@router.patch("/workflows/{workflow_id}/milestones/reorder")
async def reorder_workflow_milestones(
    workflow_id: int,
    reorder_request: MilestoneReorderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Riordina milestone di un workflow"""
    try:
        # Verifica che il workflow esista
        workflow_check = db.execute(
            text("SELECT id FROM workflow_templates WHERE id = :workflow_id"),
            {"workflow_id": workflow_id}
        ).fetchone()
        
        if not workflow_check:
            raise HTTPException(status_code=404, detail="Workflow non trovato")
        
        # Aggiorna ordine milestone
        for item in reorder_request.milestone_orders:
            milestone_id = item.get("milestone_id")
            new_order = item.get("ordine")
            
            if milestone_id and new_order is not None:
                update_query = """
                UPDATE workflow_milestones 
                SET ordine = :new_order 
                WHERE id = :milestone_id AND workflow_template_id = :workflow_id
                """
                
                db.execute(text(update_query), {
                    "new_order": new_order,
                    "milestone_id": milestone_id,
                    "workflow_id": workflow_id
                })
        
        db.commit()
        
        return {
            "message": "Ordine milestone aggiornato",
            "workflow_id": workflow_id,
            "updated_milestones": len(reorder_request.milestone_orders)
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore riordinamento milestone: {str(e)}")

@router.get("/workflows/{workflow_id}/validate", response_model=WorkflowValidationResponse)
async def validate_workflow(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Valida la configurazione di un workflow"""
    try:
        errors = []
        warnings = []
        statistics = {}
        
        # Verifica workflow
        workflow_query = """
        SELECT * FROM workflow_templates WHERE id = :workflow_id
        """
        workflow = db.execute(text(workflow_query), {"workflow_id": workflow_id}).fetchone()
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow non trovato")
        
        # Verifica milestone
        milestones_query = """
        SELECT * FROM workflow_milestones 
        WHERE workflow_template_id = :workflow_id 
        ORDER BY ordine
        """
        milestones = db.execute(text(milestones_query), {"workflow_id": workflow_id}).fetchall()
        
        statistics["total_milestones"] = len(milestones)
        
        if len(milestones) == 0:
            errors.append("Workflow senza milestone")
        else:
            # Verifica ordine milestone
            expected_order = 1
            for milestone in milestones:
                if milestone.ordine != expected_order:
                    warnings.append(f"Milestone '{milestone.nome}' ha ordine {milestone.ordine}, atteso {expected_order}")
                expected_order += 1
            
            # Verifica task per ogni milestone
            total_tasks = 0
            milestones_without_tasks = 0
            
            for milestone in milestones:
                tasks_query = """
                SELECT COUNT(*) as task_count 
                FROM milestone_task_templates 
                WHERE milestone_id = :milestone_id
                """
                task_count = db.execute(text(tasks_query), {"milestone_id": milestone.id}).fetchone().task_count
                
                total_tasks += task_count
                
                if task_count == 0:
                    milestones_without_tasks += 1
                    warnings.append(f"Milestone '{milestone.nome}' senza task configurati")
            
            statistics["total_tasks"] = total_tasks
            statistics["milestones_without_tasks"] = milestones_without_tasks
            statistics["avg_tasks_per_milestone"] = round(total_tasks / len(milestones), 2)
        
        # Verifica durate
        total_duration = sum(m.durata_stimata_giorni or 0 for m in milestones)
        statistics["total_estimated_days"] = total_duration
        
        if workflow.durata_stimata_giorni and total_duration != workflow.durata_stimata_giorni:
            warnings.append(f"Durata workflow ({workflow.durata_stimata_giorni}g) != somma milestone ({total_duration}g)")
        
        # Verifica SLA
        total_sla = sum(m.sla_giorni or 0 for m in milestones)
        statistics["total_sla_days"] = total_sla
        
        is_valid = len(errors) == 0
        
        return WorkflowValidationResponse(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            statistics=statistics
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore validazione workflow: {str(e)}")

@router.get("/workflows/{workflow_id}/export")
async def export_workflow_config(
    workflow_id: int,
    format: str = Query("json", regex="^(json|yaml)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Esporta configurazione workflow"""
    try:
        # Recupera workflow completo
        workflow_query = """
        SELECT wt.*, a.nome as articolo_nome, a.codice as articolo_codice
        FROM workflow_templates wt
        LEFT JOIN articoli a ON wt.articolo_id = a.id
        WHERE wt.id = :workflow_id
        """
        workflow = db.execute(text(workflow_query), {"workflow_id": workflow_id}).fetchone()
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow non trovato")
        
        # Recupera milestone e task
        milestones_query = """
        SELECT wm.*, 
               (SELECT json_agg(
                   json_build_object(
                       'id', mtt.id,
                       'nome', mtt.nome,
                       'descrizione', mtt.descrizione,
                       'ordine', mtt.ordine,
                       'durata_stimata_ore', mtt.durata_stimata_ore,
                       'ruolo_responsabile', mtt.ruolo_responsabile,
                       'obbligatorio', mtt.obbligatorio,
                       'tipo_task', mtt.tipo_task,
                       'checklist_template', mtt.checklist_template
                   ) ORDER BY mtt.ordine
               ) FROM milestone_task_templates mtt WHERE mtt.milestone_id = wm.id) as task_templates
        FROM workflow_milestones wm
        WHERE wm.workflow_template_id = :workflow_id
        ORDER BY wm.ordine
        """
        milestones = db.execute(text(milestones_query), {"workflow_id": workflow_id}).fetchall()
        
        # Costruisci export data
        export_data = {
            "workflow": {
                "id": workflow.id,
                "nome": workflow.nome,
                "descrizione": workflow.descrizione,
                "articolo": {
                    "id": workflow.articolo_id,
                    "nome": workflow.articolo_nome,
                    "codice": workflow.articolo_codice
                },
                "durata_stimata_giorni": workflow.durata_stimata_giorni,
                "wkf_code": workflow.wkf_code,
                "wkf_description": workflow.wkf_description,
                "created_at": workflow.created_at.isoformat() if workflow.created_at else None
            },
            "milestones": []
        }
        
        for milestone in milestones:
            milestone_data = {
                "id": milestone.id,
                "nome": milestone.nome,
                "descrizione": milestone.descrizione,
                "ordine": milestone.ordine,
                "durata_stimata_giorni": milestone.durata_stimata_giorni,
                "sla_giorni": milestone.sla_giorni,
                "warning_giorni": milestone.warning_giorni,
                "escalation_giorni": milestone.escalation_giorni,
                "tipo_milestone": milestone.tipo_milestone,
                "auto_generate_tickets": milestone.auto_generate_tickets,
                "task_templates": milestone.task_templates or []
            }
            export_data["milestones"].append(milestone_data)
        
        export_data["export_metadata"] = {
            "exported_at": datetime.now().isoformat(),
            "exported_by": current_user.email if hasattr(current_user, 'email') else str(current_user.id),
            "total_milestones": len(milestones),
            "total_tasks": sum(len(m.task_templates or []) for m in milestones)
        }
        
        if format == "yaml":
            import yaml
            return {"content": yaml.dump(export_data, default_flow_style=False), "format": "yaml"}
        else:
            return {"content": export_data, "format": "json"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore export workflow: {str(e)}")

@router.get("/statistics/overview")
async def get_workflow_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Statistiche generali sistema workflow"""
    try:
        stats_query = """
        SELECT 
            (SELECT COUNT(*) FROM workflow_templates WHERE attivo = true) as active_workflows,
            (SELECT COUNT(*) FROM workflow_milestones) as total_milestones,
            (SELECT COUNT(*) FROM milestone_task_templates) as total_task_templates,
            (SELECT COUNT(*) FROM articoli WHERE attivo = true) as active_articoli,
            (SELECT COUNT(*) FROM kit_commerciali WHERE attivo = true) as active_kits,
            (SELECT COUNT(DISTINCT workflow_template_id) FROM workflow_milestones) as workflows_with_milestones,
            (SELECT COUNT(DISTINCT milestone_id) FROM milestone_task_templates) as milestones_with_tasks
        """
        
        result = db.execute(text(stats_query)).fetchone()
        
        # Statistiche utilizzo (placeholder - da implementare quando ci saranno dati operativi)
        usage_stats = {
            "workflows_in_use": 0,  # workflow utilizzati in ticket attivi
            "most_used_milestone": None,
            "avg_workflow_completion_days": 0
        }
        
        return {
            "configuration_stats": {
                "active_workflows": result.active_workflows,
                "total_milestones": result.total_milestones,
                "total_task_templates": result.total_task_templates,
                "active_articoli": result.active_articoli,
                "active_kits": result.active_kits,
                "workflows_with_milestones": result.workflows_with_milestones,
                "milestones_with_tasks": result.milestones_with_tasks,
                "configuration_completeness": round(
                    (result.workflows_with_milestones / max(result.active_workflows, 1)) * 100, 2
                )
            },
            "usage_stats": usage_stats,
            "recommendations": _generate_recommendations(result)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore recupero statistiche: {str(e)}")

def _generate_recommendations(stats):
    """Genera raccomandazioni basate sulle statistiche"""
    recommendations = []
    
    if stats.active_workflows == 0:
        recommendations.append("Creare almeno un workflow template per iniziare")
    elif stats.workflows_with_milestones < stats.active_workflows:
        recommendations.append("Configurare milestone per tutti i workflow attivi")
    
    if stats.total_milestones > 0 and stats.milestones_with_tasks < stats.total_milestones:
        recommendations.append("Aggiungere task template alle milestone senza configurazione")
    
    if stats.active_articoli > stats.active_workflows:
        recommendations.append("Considerare la creazione di workflow per articoli non coperti")
    
    return recommendations
