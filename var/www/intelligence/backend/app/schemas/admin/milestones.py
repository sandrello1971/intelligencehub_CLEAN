# schemas/admin/milestones.py
# Pydantic schemas per Milestones - IntelligenceHUB

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime

class MilestoneBase(BaseModel):
    """Base schema per milestones"""
    nome: str = Field(..., min_length=1, max_length=255, description="Nome milestone")
    descrizione: Optional[str] = Field(None, description="Descrizione milestone")
    tipo_commessa_id: Optional[str] = Field(None, description="ID tipo commessa")
    
    # Date
    data_inizio: Optional[datetime] = Field(None, description="Data inizio pianificata")
    data_fine_prevista: Optional[datetime] = Field(None, description="Data fine prevista")
    
    # SLA e configurazione
    sla_hours: int = Field(48, ge=1, description="SLA in ore")
    warning_days: int = Field(3, ge=0, description="Giorni di preavviso")
    escalation_days: int = Field(7, ge=0, description="Giorni per escalation")
    
    # Automazione
    auto_generate_tickets: bool = Field(False, description="Genera ticket automaticamente")
    template_data: Optional[Dict[str, Any]] = Field(None, description="Dati template JSON")
    
    # Stato
    stato: str = Field("pianificata", description="Stato milestone")
    percentuale_completamento: float = Field(0.0, ge=0.0, le=100.0, description="% completamento")

    @validator('nome')
    def validate_nome(cls, v):
        if v:
            v = v.strip()
            if len(v) < 1:
                raise ValueError('Nome milestone non può essere vuoto')
        return v

    @validator('stato')
    def validate_stato(cls, v):
        valid_stati = ['pianificata', 'in_corso', 'completata', 'in_ritardo', 'cancellata']
        if v not in valid_stati:
            raise ValueError(f'Stato deve essere uno di: {", ".join(valid_stati)}')
        return v

class MilestoneCreate(MilestoneBase):
    """Schema per creazione milestone"""
    pass

class MilestoneUpdate(BaseModel):
    """Schema per aggiornamento milestone"""
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    descrizione: Optional[str] = None
    tipo_commessa_id: Optional[str] = None
    data_inizio: Optional[datetime] = None
    data_fine_prevista: Optional[datetime] = None
    data_fine_effettiva: Optional[datetime] = None
    sla_hours: Optional[int] = Field(None, ge=1)
    warning_days: Optional[int] = Field(None, ge=0)
    escalation_days: Optional[int] = Field(None, ge=0)
    auto_generate_tickets: Optional[bool] = None
    template_data: Optional[Dict[str, Any]] = None
    stato: Optional[str] = None
    percentuale_completamento: Optional[float] = Field(None, ge=0.0, le=100.0)

    @validator('nome')
    def validate_nome(cls, v):
        if v:
            v = v.strip()
            if len(v) < 1:
                raise ValueError('Nome milestone non può essere vuoto')
        return v

    @validator('stato')
    def validate_stato(cls, v):
        if v:
            valid_stati = ['pianificata', 'in_corso', 'completata', 'in_ritardo', 'cancellata']
            if v not in valid_stati:
                raise ValueError(f'Stato deve essere uno di: {", ".join(valid_stati)}')
        return v

class Milestone(MilestoneBase):
    """Schema per lettura milestone"""
    id: int
    data_fine_effettiva: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None

    class Config:
        orm_mode = True

class MilestoneInDB(Milestone):
    """Schema completo per database"""
    pass
