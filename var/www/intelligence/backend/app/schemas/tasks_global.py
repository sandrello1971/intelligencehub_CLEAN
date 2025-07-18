"""
Intelligence API - Tasks Global Schemas
Pydantic schemas per modelli di task riutilizzabili
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TaskGlobalBase(BaseModel):
    """Schema base per modelli task"""
    tsk_code: str = Field(..., min_length=1, max_length=50, description="Codice task")
    tsk_description: Optional[str] = Field(None, description="Descrizione task")
    tsk_type: str = Field("template", description="Tipo task")
    tsk_category: Optional[str] = Field(None, max_length=50, description="Categoria task")
    sla_giorni: Optional[int] = Field(None, ge=1, le=365, description="SLA in giorni")
    warning_giorni: int = Field(1, ge=0, le=30, description="Warning giorni prima")
    escalation_giorni: int = Field(1, ge=0, le=30, description="Escalation giorni dopo")
    priorita: str = Field("normale", pattern="^(bassa|normale|alta|critica)$", description="Priorità")

class TaskGlobalCreate(TaskGlobalBase):
    """Schema per creazione modello task"""
    pass

class TaskGlobalUpdate(BaseModel):
    """Schema per aggiornamento modello task"""
    tsk_code: Optional[str] = Field(None, min_length=1, max_length=50)
    tsk_description: Optional[str] = None
    tsk_type: Optional[str] = None
    tsk_category: Optional[str] = Field(None, max_length=50)
    sla_giorni: Optional[int] = Field(None, ge=1, le=365)
    warning_giorni: Optional[int] = Field(None, ge=0, le=30)
    escalation_giorni: Optional[int] = Field(None, ge=0, le=30)
    priorita: Optional[str] = Field(None, pattern="^(bassa|normale|alta|critica)$")

class TaskGlobalResponse(TaskGlobalBase):
    """Schema per risposta modello task"""
    id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
