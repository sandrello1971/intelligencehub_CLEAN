from pydantic import validator
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class TaskTemplateBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=200)
    descrizione: Optional[str] = None
    checklist: Optional[List[str]] = []
    tempo_stimato: Optional[int] = None  # minuti
    priority: str = Field(default="medium")

    @validator("priority", pre=True)
    def map_italian_priority(cls, v):
        if v is None:
            return v
        priority_mapping = {
            "Alta": "high",
            "Media": "medium",
            "Bassa": "low"
        }
        return priority_mapping.get(v, v)
    categoria: Optional[str] = None

class TaskTemplateCreate(TaskTemplateBase):
    pass

class TaskTemplateUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=200)
    descrizione: Optional[str] = None
    checklist: Optional[List[str]] = None
    tempo_stimato: Optional[int] = None
    priority: Optional[str] = Field(None)
    categoria: Optional[str] = None

class TaskTemplateResponse(TaskTemplateBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class TicketTemplateBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=200)
    descrizione: Optional[str] = None
    categoria: Optional[str] = None
    priority: str = Field(default="medium")

    @validator("priority", pre=True)
    def map_italian_priority(cls, v):
        if v is None:
            return v
        priority_mapping = {
            "Alta": "high",
            "Media": "medium",
            "Bassa": "low"
        }
        return priority_mapping.get(v, v)
    task_templates: Optional[List[int]] = []  # IDs dei task template
    articolo_id: Optional[int] = None
    workflow_template_id: Optional[int] = None
    auto_assign_rules: Optional[dict] = {}
    template_description: Optional[str] = None
    is_active: bool = True

class TicketTemplateCreate(TicketTemplateBase):
    pass

class TicketTemplateUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=200)
    descrizione: Optional[str] = None
    categoria: Optional[str] = None
    priority: Optional[str] = Field(None)
    task_templates: Optional[List[int]] = None
    articolo_id: Optional[int] = None
    workflow_template_id: Optional[int] = None
    auto_assign_rules: Optional[dict] = None
    template_description: Optional[str] = None
    is_active: Optional[bool] = None

class TicketTemplateResponse(TicketTemplateBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Alias per compatibilità con i nomi nei routes
ModelloTaskCreate = TaskTemplateCreate
ModelloTaskUpdate = TaskTemplateUpdate
ModelloTaskResponse = TaskTemplateResponse

ModelloTicketCreate = TicketTemplateCreate
ModelloTicketUpdate = TicketTemplateUpdate
ModelloTicketResponse = TicketTemplateResponse

# Classe per lista items
class TemplateListItem(BaseModel):
    id: UUID
    nome: str
    categoria: Optional[str] = None
    
    class Config:
        from_attributes = True
