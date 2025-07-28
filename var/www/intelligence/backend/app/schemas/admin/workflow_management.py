# schemas/admin/workflow_management.py  
# Schema per gestire l'architettura esistente - IntelligenceHUB

from pydantic import BaseModel, Field, validator
from uuid import UUID
from typing import Optional, List, Dict, Any
from datetime import datetime

# ===== ARTICOLI SCHEMAS =====
class ArticoloBase(BaseModel):
    """Schema per articoli (servizi base)"""
    codice: str = Field(..., max_length=10, description="Codice articolo")
    nome: str = Field(..., max_length=200, description="Nome articolo")
    descrizione: Optional[str] = Field(None, description="Descrizione")
    tipo_prodotto: str = Field(..., description="semplice o composito")
    prezzo_base: Optional[float] = Field(None, description="Prezzo base")
    durata_mesi: Optional[int] = Field(None, description="Durata mesi")
    sla_default_hours: int = Field(48, description="SLA default ore")
    template_milestones: Optional[Dict[str, Any]] = Field(None, description="Template milestone JSON")
    attivo: bool = Field(True, description="Articolo attivo")

    @validator('tipo_prodotto')
    def validate_tipo_prodotto(cls, v):
        if v not in ['semplice', 'composito']:
            raise ValueError('tipo_prodotto deve essere semplice o composito')
        return v

class ArticoloResponse(ArticoloBase):
    """Schema risposta articolo"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ===== KIT COMMERCIALI SCHEMAS =====
class KitCommercialeBase(BaseModel):
    """Schema per kit commerciali"""
    nome: str = Field(..., max_length=200, description="Nome kit")
    descrizione: Optional[str] = Field(None, description="Descrizione kit")
    articolo_principale_id: Optional[int] = Field(None, description="ID articolo principale")
    attivo: bool = Field(True, description="Kit attivo")

class KitCommercialeResponse(KitCommercialeBase):
    """Schema risposta kit commerciale"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ===== WORKFLOW TEMPLATES SCHEMAS =====
class WorkflowTemplateBase(BaseModel):
    """Schema per workflow template"""
    nome: str = Field(..., max_length=200, description="Nome workflow")
    descrizione: Optional[str] = Field(None, description="Descrizione workflow")
    durata_stimata_giorni: Optional[int] = Field(None, description="Durata stimata giorni")
    ordine: int = Field(0, description="Ordine workflow")
    wkf_code: Optional[str] = Field(None, max_length=50, description="Codice workflow")
    wkf_description: Optional[str] = Field(None, description="Descrizione dettagliata")
    attivo: bool = Field(True, description="Workflow attivo")

class WorkflowTemplateCreate(WorkflowTemplateBase):
    """Schema creazione workflow template"""
    pass

class WorkflowTemplateResponse(WorkflowTemplateBase):
    """Schema risposta workflow template"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ===== WORKFLOW MILESTONES SCHEMAS =====
class WorkflowMilestoneBase(BaseModel):
    """Schema per milestone di workflow"""
    workflow_template_id: int = Field(..., description="ID workflow template")
    nome: str = Field(..., max_length=200, description="Nome milestone")
    descrizione: Optional[str] = Field(None, description="Descrizione milestone")
    ordine: int = Field(..., description="Ordine milestone nel workflow")
    durata_stimata_giorni: Optional[int] = Field(None, description="Durata stimata giorni")
    sla_giorni: Optional[int] = Field(None, description="SLA giorni")
    warning_giorni: int = Field(2, description="Giorni warning")
    escalation_giorni: int = Field(1, description="Giorni escalation")
    tipo_milestone: str = Field("standard", description="Tipo milestone")
    auto_generate_tickets: bool = Field(True, description="Auto genera ticket")

class WorkflowMilestoneCreate(WorkflowMilestoneBase):
    """Schema creazione milestone workflow"""
    pass

class WorkflowMilestoneResponse(WorkflowMilestoneBase):
    """Schema risposta milestone workflow"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ===== MILESTONE TASK TEMPLATES SCHEMAS =====
class MilestoneTaskTemplateBase(BaseModel):
    """Schema per task template di milestone"""
    milestone_id: int = Field(..., description="ID workflow milestone")
    nome: str = Field(..., max_length=200, description="Nome task template")
    descrizione: Optional[str] = Field(None, description="Descrizione task")
    ordine: int = Field(0, description="Ordine task")
    durata_stimata_ore: Optional[int] = Field(None, description="Durata stimata ore")
    ruolo_responsabile: Optional[str] = Field(None, max_length=100, description="Ruolo responsabile")
    obbligatorio: bool = Field(True, description="Task obbligatorio")
    tipo_task: str = Field("standard", description="Tipo task")
    checklist_template: List[Dict[str, Any]] = Field(default=[], description="Template checklist")

class MilestoneTaskTemplateCreate(MilestoneTaskTemplateBase):
    """Schema creazione task template"""
    pass

class MilestoneTaskTemplateResponse(MilestoneTaskTemplateBase):
    """Schema risposta task template"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ===== COMPOSITE SCHEMAS =====
class WorkflowTemplateWithMilestones(WorkflowTemplateResponse):
    """Workflow template con milestone associate"""
    milestones: List[WorkflowMilestoneResponse] = Field(default=[], description="Milestone del workflow")

class WorkflowMilestoneWithTasks(WorkflowMilestoneResponse):
    """Milestone con task template associati"""
    task_templates: List[MilestoneTaskTemplateResponse] = Field(default=[], description="Task template della milestone")

# ===== TICKET TEMPLATE SERVIZI SCHEMAS =====
class TicketTemplateServizioBase(BaseModel):
    """Schema per associazione ticket template - servizi"""
    ticket_template_id: UUID = Field(..., description="ID ticket template")
    articolo_id: Optional[int] = Field(None, description="ID articolo servizio")
    kit_commerciale_id: Optional[int] = Field(None, description="ID kit commerciale")

class TicketTemplateServizioCreate(TicketTemplateServizioBase):
    """Schema creazione associazione ticket-servizio"""
    pass

class TicketTemplateServizioResponse(TicketTemplateServizioBase):
    """Schema risposta associazione ticket-servizio"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class CompleteWorkflowResponse(WorkflowTemplateResponse):
    """Workflow completo con milestone e task"""
    milestones: List[WorkflowMilestoneWithTasks] = Field(default=[], description="Milestone complete")
