# routes/admin/workflow_config.py
# API Routes per Configurazione Workflow Esistenti - IntelligenceHUB

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.routes.auth import get_current_user_dep
from app.schemas.admin.workflow_management import (
    ArticoloResponse, KitCommercialeResponse,
    WorkflowTemplateCreate, WorkflowTemplateResponse, WorkflowTemplateWithMilestones,
    WorkflowMilestoneCreate, WorkflowMilestoneResponse, WorkflowMilestoneWithTasks,
    MilestoneTaskTemplateCreate, MilestoneTaskTemplateResponse,
    CompleteWorkflowResponse
)
from app.models.users import User

router = APIRouter(prefix="/api/v1/admin/workflow-config", tags=["Workflow Configuration"])

# ===== ARTICOLI ENDPOINTS =====

@router.get("/articoli", response_model=List[ArticoloResponse])
async def list_articoli(
    attivo: bool = Query(True),
    tipo_prodotto: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Lista articoli (servizi base) disponibili"""
    try:
        query = """
        SELECT id, codice, nome, descrizione, tipo_prodotto, prezzo_base,
               durata_mesi, sla_default_hours, template_milestones, attivo,
               created_at, updated_at
        FROM articoli 
        WHERE attivo = :attivo
        """
        params = {"attivo": attivo}
        
        if tipo_prodotto:
            query += " AND tipo_prodotto = :tipo_prodotto"
            params["tipo_prodotto"] = tipo_prodotto
            
        query += " ORDER BY codice, nome"
        
        result = db.execute(text(query), params).fetchall()
        
        articoli = []
        for row in result:
            articolo = ArticoloResponse(
                id=row.id,
                codice=row.codice,
                nome=row.nome,
                descrizione=row.descrizione,
                tipo_prodotto=row.tipo_prodotto,
                prezzo_base=float(row.prezzo_base) if row.prezzo_base else None,
                durata_mesi=row.durata_mesi,
                sla_default_hours=row.sla_default_hours,
                template_milestones=row.template_milestones,
                attivo=row.attivo,
                created_at=row.created_at,
                updated_at=row.updated_at
            )
            articoli.append(articolo)
        
        return articoli
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore recupero articoli: {str(e)}")

@router.get("/articoli/{articolo_id}", response_model=ArticoloResponse)
async def get_articolo(
    articolo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Recupera dettaglio articolo"""
    try:
        query = """
        SELECT id, codice, nome, descrizione, tipo_prodotto, prezzo_base,
               durata_mesi, sla_default_hours, template_milestones, attivo,
               created_at, updated_at
        FROM articoli 
        WHERE id = :articolo_id
        """
        
        result = db.execute(text(query), {"articolo_id": articolo_id}).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Articolo non trovato")
        
        return ArticoloResponse(
            id=result.id,
            codice=result.codice,
            nome=result.nome,
            descrizione=result.descrizione,
            tipo_prodotto=result.tipo_prodotto,
            prezzo_base=float(result.prezzo_base) if result.prezzo_base else None,
            durata_mesi=result.durata_mesi,
            sla_default_hours=result.sla_default_hours,
            template_milestones=result.template_milestones,
            attivo=result.attivo,
            created_at=result.created_at,
            updated_at=result.updated_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore recupero articolo: {str(e)}")

# ===== KIT COMMERCIALI ENDPOINTS =====

@router.get("/kit-commerciali", response_model=List[KitCommercialeResponse])
async def list_kit_commerciali(
    attivo: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Lista kit commerciali disponibili"""
    try:
        query = """
        SELECT kc.id, kc.nome, kc.descrizione, kc.articolo_principale_id, 
               kc.attivo, kc.created_at,
               a.nome as articolo_principale_nome
        FROM kit_commerciali kc
        LEFT JOIN articoli a ON kc.articolo_principale_id = a.id
        WHERE kc.attivo = :attivo
        ORDER BY kc.nome
        """
        
        result = db.execute(text(query), {"attivo": attivo}).fetchall()
        
        kits = []
        for row in result:
            kit = KitCommercialeResponse(
                id=row.id,
                nome=row.nome,
                descrizione=row.descrizione,
                articolo_principale_id=row.articolo_principale_id,
                attivo=row.attivo,
                created_at=row.created_at
            )
            kits.append(kit)
        
        return kits
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore recupero kit commerciali: {str(e)}")

# ===== WORKFLOW TEMPLATES ENDPOINTS =====

@router.post("/workflow-templates", response_model=WorkflowTemplateResponse)
async def create_workflow_template(
    workflow_data: WorkflowTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Crea nuovo workflow template"""
    try:
        query = """
        INSERT INTO workflow_templates 
        (nome, descrizione,  durata_stimata_giorni, ordine, wkf_code, wkf_description, attivo)
        VALUES 
        (:nome, :descrizione,  :durata_stimata_giorni, :ordine, :wkf_code, :wkf_description, :attivo)
        RETURNING id, created_at
        """
        
        result = db.execute(text(query), {
            "nome": workflow_data.nome,
            "descrizione": workflow_data.descrizione,
            "durata_stimata_giorni": workflow_data.durata_stimata_giorni,
            "ordine": workflow_data.ordine,
            "wkf_code": workflow_data.wkf_code,
            "wkf_description": workflow_data.wkf_description,
            "attivo": workflow_data.attivo
        }).fetchone()
        
        db.commit()
        
        return WorkflowTemplateResponse(
            id=result.id,
            nome=workflow_data.nome,
            descrizione=workflow_data.descrizione,
            durata_stimata_giorni=workflow_data.durata_stimata_giorni,
            ordine=workflow_data.ordine,
            wkf_code=workflow_data.wkf_code,
            wkf_description=workflow_data.wkf_description,
            attivo=workflow_data.attivo,
            created_at=result.created_at
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore creazione workflow template: {str(e)}")

@router.patch("/workflow-templates/{template_id}", response_model=WorkflowTemplateResponse)
async def update_workflow_template(
    template_id: int,
    workflow_data: WorkflowTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Aggiorna workflow template esistente"""
    try:
        # Verifica che il workflow esista
        check_query = "SELECT id FROM workflow_templates WHERE id = :id"
        existing = db.execute(text(check_query), {"id": template_id}).fetchone()
        
        if not existing:
            raise HTTPException(status_code=404, detail="Workflow non trovato")
        
        # Aggiorna workflow
        update_query = """
        UPDATE workflow_templates 
        SET nome = :nome, descrizione = :descrizione, 
            durata_stimata_giorni = :durata_stimata_giorni, ordine = :ordine,
            wkf_code = :wkf_code, wkf_description = :wkf_description, attivo = :attivo
        WHERE id = :id
        """
        
        db.execute(text(update_query), {
            "id": template_id,
            "nome": workflow_data.nome,
            "descrizione": workflow_data.descrizione,
            "durata_stimata_giorni": workflow_data.durata_stimata_giorni,
            "ordine": workflow_data.ordine,
            "wkf_code": workflow_data.wkf_code,
            "wkf_description": workflow_data.wkf_description,
            "attivo": workflow_data.attivo
        })
        
        db.commit()
        
        # Recupera il workflow aggiornato
        get_query = "SELECT * FROM workflow_templates WHERE id = :id"
        result = db.execute(text(get_query), {"id": template_id}).fetchone()
        
        return WorkflowTemplateResponse(
            id=result.id,
            nome=result.nome,
            descrizione=result.descrizione,
            durata_stimata_giorni=result.durata_stimata_giorni,
            ordine=result.ordine,
            wkf_code=result.wkf_code,
            wkf_description=result.wkf_description,
            attivo=result.attivo,
            created_at=result.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore aggiornamento workflow: {str(e)}")

@router.get("/workflow-templates", response_model=List[WorkflowTemplateResponse])
async def list_workflow_templates(
    articolo_id: Optional[int] = Query(None),
    attivo: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Lista workflow templates"""
    try:
        query = """
        SELECT wt.id, wt.nome, wt.descrizione, wt.durata_stimata_giorni,
               wt.ordine, wt.wkf_code, wt.wkf_description, wt.attivo, wt.created_at
        FROM workflow_templates wt
        WHERE wt.attivo = :attivo
        """
        
        params = {"attivo": attivo}
        
        if articolo_id:
            query += " AND wt.articolo_id = :articolo_id"
            params["articolo_id"] = articolo_id
            
        query += " ORDER BY wt.ordine, wt.nome"
        
        result = db.execute(text(query), params).fetchall()
        
        workflows = []
        for row in result:
            workflow = WorkflowTemplateResponse(
                id=row.id,
                nome=row.nome,
                descrizione=row.descrizione,
                durata_stimata_giorni=row.durata_stimata_giorni,
                ordine=row.ordine,
                wkf_code=row.wkf_code,
                wkf_description=row.wkf_description,
                attivo=row.attivo,
                created_at=row.created_at
            )
            workflows.append(workflow)
        
        return workflows
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore recupero workflow templates: {str(e)}")

@router.delete("/workflow-templates/{template_id}")
async def delete_workflow_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Elimina workflow template"""
    try:
        # Verifica che il workflow esista
        workflow_check = db.execute(text("SELECT id FROM workflow_templates WHERE id = :id"), {"id": template_id}).fetchone()
        if not workflow_check:
            raise HTTPException(status_code=404, detail="Workflow non trovato")
        
        # Elimina prima le milestone associate
        db.execute(text("DELETE FROM milestone_task_templates WHERE milestone_id IN (SELECT id FROM workflow_milestones WHERE workflow_template_id = :workflow_id)"), {"workflow_id": template_id})
        db.execute(text("DELETE FROM workflow_milestones WHERE workflow_template_id = :workflow_id"), {"workflow_id": template_id})
        
        # Elimina il workflow
        result = db.execute(text("DELETE FROM workflow_templates WHERE id = :id"), {"id": template_id})
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Workflow non trovato")
        
        db.commit()
        return {"message": "Workflow eliminato con successo"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore eliminazione workflow: {str(e)}")


@router.get("/workflow-templates/{template_id}", response_model=CompleteWorkflowResponse)
async def get_complete_workflow(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Recupera workflow completo con milestone e task"""
    try:
        # Recupera workflow template
        workflow_query = """
        SELECT id, nome, descrizione, durata_stimata_giorni,
               ordine, wkf_code, wkf_description, attivo, created_at
        FROM workflow_templates 
        WHERE id = :template_id
        """
        
        workflow_result = db.execute(text(workflow_query), {"template_id": template_id}).fetchone()
        
        if not workflow_result:
            raise HTTPException(status_code=404, detail="Workflow template non trovato")
        
        # Recupera milestone del workflow
        milestones_query = """
        SELECT wm.id, wm.workflow_template_id, wm.nome, wm.descrizione, wm.ordine,
               wm.durata_stimata_giorni, wm.sla_giorni, wm.warning_giorni, 
               wm.escalation_giorni, wm.tipo_milestone, wm.auto_generate_tickets, wm.created_at
        FROM workflow_milestones wm
        WHERE wm.workflow_template_id = :template_id
        ORDER BY wm.ordine
        """
        
        milestones_result = db.execute(text(milestones_query), {"template_id": template_id}).fetchall()
        
        milestones_with_tasks = []
        for milestone_row in milestones_result:
            # Recupera task template per ogni milestone
            tasks_query = """
            SELECT id, milestone_id, nome, descrizione, ordine, durata_stimata_ore,
                   ruolo_responsabile, obbligatorio, tipo_task, checklist_template, created_at
            FROM milestone_task_templates
            WHERE milestone_id = :milestone_id
            ORDER BY ordine
            """
            
            tasks_result = db.execute(text(tasks_query), {"milestone_id": milestone_row.id}).fetchall()
            
            task_templates = []
            for task_row in tasks_result:
                task = MilestoneTaskTemplateResponse(
                    id=task_row.id,
                    milestone_id=task_row.milestone_id,
                    nome=task_row.nome,
                    descrizione=task_row.descrizione,
                    ordine=task_row.ordine,
                    durata_stimata_ore=task_row.durata_stimata_ore,
                    ruolo_responsabile=task_row.ruolo_responsabile,
                    obbligatorio=task_row.obbligatorio,
                    tipo_task=task_row.tipo_task,
                    checklist_template=task_row.checklist_template or [],
                    created_at=task_row.created_at
                )
                task_templates.append(task)
            
            milestone_with_tasks = WorkflowMilestoneWithTasks(
                id=milestone_row.id,
                workflow_template_id=milestone_row.workflow_template_id,
                nome=milestone_row.nome,
                descrizione=milestone_row.descrizione,
                ordine=milestone_row.ordine,
                durata_stimata_giorni=milestone_row.durata_stimata_giorni,
                sla_giorni=milestone_row.sla_giorni,
                warning_giorni=milestone_row.warning_giorni,
                escalation_giorni=milestone_row.escalation_giorni,
                tipo_milestone=milestone_row.tipo_milestone,
                auto_generate_tickets=milestone_row.auto_generate_tickets,
                created_at=milestone_row.created_at,
                task_templates=task_templates
            )
            milestones_with_tasks.append(milestone_with_tasks)
        
        return CompleteWorkflowResponse(
            id=workflow_result.id,
            nome=workflow_result.nome,
            descrizione=workflow_result.descrizione,
            durata_stimata_giorni=workflow_result.durata_stimata_giorni,
            ordine=workflow_result.ordine,
            wkf_code=workflow_result.wkf_code,
            wkf_description=workflow_result.wkf_description,
            attivo=workflow_result.attivo,
            created_at=workflow_result.created_at,
            milestones=milestones_with_tasks
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore recupero workflow completo: {str(e)}")

# ===== WORKFLOW MILESTONES ENDPOINTS =====

@router.post("/workflow-milestones", response_model=WorkflowMilestoneResponse)
async def create_workflow_milestone(
    milestone_data: WorkflowMilestoneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Crea nuova milestone per workflow"""
    try:
        query = """
        INSERT INTO workflow_milestones 
        (workflow_template_id, nome, descrizione, ordine, durata_stimata_giorni, 
         sla_giorni, warning_giorni, escalation_giorni, tipo_milestone, auto_generate_tickets)
        VALUES 
        (:workflow_template_id, :nome, :descrizione, :ordine, :durata_stimata_giorni,
         :sla_giorni, :warning_giorni, :escalation_giorni, :tipo_milestone, :auto_generate_tickets)
        RETURNING id, created_at
        """
        
        result = db.execute(text(query), milestone_data.dict()).fetchone()
        db.commit()
        
        return WorkflowMilestoneResponse(
            id=result.id,
            created_at=result.created_at,
            **milestone_data.dict()
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore creazione milestone: {str(e)}")

# ===== MILESTONE TASK TEMPLATES ENDPOINTS =====

@router.post("/milestone-task-templates", response_model=MilestoneTaskTemplateResponse)
async def create_milestone_task_template(
    task_data: MilestoneTaskTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Crea nuovo task template per milestone"""
    try:
        query = """
        INSERT INTO milestone_task_templates 
        (milestone_id, nome, descrizione, ordine, durata_stimata_ore, 
         ruolo_responsabile, obbligatorio, tipo_task, checklist_template)
        VALUES 
        (:milestone_id, :nome, :descrizione, :ordine, :durata_stimata_ore,
         :ruolo_responsabile, :obbligatorio, :tipo_task, :checklist_template)
        RETURNING id, created_at
        """
        
        result = db.execute(text(query), task_data.dict()).fetchone()
        db.commit()
        
        return MilestoneTaskTemplateResponse(
            id=result.id,
            created_at=result.created_at,
            **task_data.dict()
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore creazione task template: {str(e)}")

@router.get("/workflow-templates/{workflow_id}/milestones")
async def get_workflow_milestones(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Recupera milestone di un workflow template"""
    try:
        # Verifica che il workflow esista
        workflow_check = db.execute(text("SELECT id FROM workflow_templates WHERE id = :id"), {"id": workflow_id}).fetchone()
        if not workflow_check:
            raise HTTPException(status_code=404, detail="Workflow non trovato")
        
        # Recupera le milestone associate
        query = """
        SELECT wm.id, wm.nome, wm.descrizione, wm.ordine, wm.durata_stimata_giorni, 
               wm.sla_giorni, wm.tipo_milestone, wm.created_at,
               (SELECT COUNT(*) FROM milestone_task_templates WHERE milestone_id = wm.id) as task_count
        FROM workflow_milestones wm 
        WHERE wm.workflow_template_id = :workflow_id
        ORDER BY wm.ordine, wm.nome
        """
        
        result = db.execute(text(query), {"workflow_id": workflow_id}).fetchall()
        
        milestones = []
        for row in result:
            milestones.append({
                "id": row.id,
                "nome": row.nome,
                "descrizione": row.descrizione,
                "ordine": row.ordine,
                "durata_stimata_giorni": row.durata_stimata_giorni,
                "sla_giorni": row.sla_giorni,
                "tipo_milestone": row.tipo_milestone,
                "task_count": row.task_count,
                "created_at": row.created_at
            })
        
        return {"workflow_id": workflow_id, "milestones": milestones}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore: {str(e)}")

@router.post("/workflow-templates/{workflow_id}/milestones/{milestone_template_id}")
async def assign_milestone_template_to_workflow(
    workflow_id: int,
    milestone_template_id: int,
    assignment_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Associa milestone template al workflow"""
    try:
        # Verifica che il workflow esista
        workflow_check = db.execute(text("SELECT id FROM workflow_templates WHERE id = :id"), {"id": workflow_id}).fetchone()
        if not workflow_check:
            raise HTTPException(status_code=404, detail="Workflow non trovato")
        
        # Verifica che il milestone template esista (template = workflow_template_id IS NULL)
        milestone_check = db.execute(text("SELECT id, nome, descrizione, sla_giorni, tipo_milestone FROM workflow_milestones WHERE id = :id AND workflow_template_id IS NULL"), 
                                   {"id": milestone_template_id}).fetchone()
        if not milestone_check:
            raise HTTPException(status_code=404, detail="Milestone template non trovato")
        
        # Verifica che non sia già associato
        existing_check = db.execute(text("SELECT id FROM workflow_milestones WHERE workflow_template_id = :workflow_id AND nome = :nome"), 
                                  {"workflow_id": workflow_id, "nome": milestone_check.nome}).fetchone()
        if existing_check:
            raise HTTPException(status_code=400, detail="Milestone già associata al workflow")
        
        # Crea la milestone per il workflow basata sul template
        query = """
        INSERT INTO workflow_milestones 
        (workflow_template_id, nome, descrizione, ordine, durata_stimata_giorni, sla_giorni, 
         warning_giorni, escalation_giorni, tipo_milestone, auto_generate_tickets)
        VALUES (:workflow_id, :nome, :descrizione, :ordine, :durata_giorni, :sla_giorni,
                2, 1, :tipo_milestone, true)
        RETURNING id
        """
        
        result = db.execute(text(query), {
            "workflow_id": workflow_id,
            "nome": milestone_check.nome,
            "descrizione": milestone_check.descrizione,
            "ordine": assignment_data.get("ordine", 1),
            "durata_giorni": assignment_data.get("durata_stimata_giorni"),
            "sla_giorni": milestone_check.sla_giorni,
            "tipo_milestone": milestone_check.tipo_milestone
        }).fetchone()
        
        new_milestone_id = result.id
        
        # Copia anche i task template associati
        copy_tasks_query = """
        INSERT INTO milestone_task_templates 
        (milestone_id, nome, descrizione, ordine, durata_stimata_ore, ruolo_responsabile, obbligatorio, tipo_task)
        SELECT :new_milestone_id, nome, descrizione, ordine, durata_stimata_ore, ruolo_responsabile, obbligatorio, tipo_task
        FROM milestone_task_templates 
        WHERE milestone_id = :template_milestone_id
        """
        
        db.execute(text(copy_tasks_query), {
            "new_milestone_id": new_milestone_id,
            "template_milestone_id": milestone_template_id
        })
        
        db.commit()
        return {"message": "Milestone template associato al workflow con successo", "new_milestone_id": new_milestone_id}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore: {str(e)}")

@router.delete("/workflow-templates/{workflow_id}/milestones/{milestone_id}")
async def remove_milestone_from_workflow(
    workflow_id: int,
    milestone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Rimuove milestone dal workflow"""
    try:
        # Elimina prima i task associati
        db.execute(text("DELETE FROM milestone_task_templates WHERE milestone_id = :milestone_id"), {"milestone_id": milestone_id})
        
        # Elimina la milestone
        result = db.execute(text("DELETE FROM workflow_milestones WHERE id = :id AND workflow_template_id = :workflow_id"), 
                          {"id": milestone_id, "workflow_id": workflow_id})
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Milestone non trovata nel workflow")
        
        db.commit()
        return {"message": "Milestone rimossa dal workflow con successo"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore: {str(e)}")
