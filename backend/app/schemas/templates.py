from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class TaskTemplateBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=200)
    descrizione: Optional[str] = None
    checklist: Optional[List[str]] = []
    tempo_stimato: Optional[int] = None  # minuti
    priorita: str = Field(default="medium", pattern="^(low|medium|high|urgent)$")
    categoria: Optional[str] = None

class TaskTemplateCreate(TaskTemplateBase):
    pass

class TaskTemplateUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=200)
    descrizione: Optional[str] = None
    checklist: Optional[List[str]] = None
    tempo_stimato: Optional[int] = None
    priorita: Optional[str] = Field(None, pattern="^(low|medium|high|urgent)$")
    categoria: Optional[str] = None

class TaskTemplateResponse(TaskTemplateBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class TicketTemplateBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=200)
    descrizione: Optional[str] = None
    categoria: Optional[str] = None
    priorita: str = Field(default="medium", pattern="^(low|medium|high|urgent)$")
    sla_ore: Optional[int] = None
    task_templates: Optional[List[int]] = []  # IDs dei task template

class TicketTemplateCreate(TicketTemplateBase):
    pass

class TicketTemplateUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=200)
    descrizione: Optional[str] = None
    categoria: Optional[str] = None
    priorita: Optional[str] = Field(None, pattern="^(low|medium|high|urgent)$")
    sla_ore: Optional[int] = None
    task_templates: Optional[List[int]] = None

class TicketTemplateResponse(TicketTemplateBase):
    id: int
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
    id: int
    nome: str
    categoria: Optional[str] = None
    
    class Config:
        from_attributes = True
