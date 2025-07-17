from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import date, datetime
from uuid import UUID

class CommessaBase(BaseModel):
    codice: str = Field(..., min_length=1, max_length=50, description="Codice univoco commessa")
    nome: str = Field(..., min_length=1, max_length=255, description="Nome commessa")
    descrizione: Optional[str] = Field(None, description="Descrizione dettagliata")
    client_id: Optional[int] = Field(None, description="ID cliente associato")
    budget: Optional[float] = Field(None, ge=0, description="Budget commessa")
    data_inizio: Optional[date] = Field(None, description="Data inizio prevista")
    data_fine_prevista: Optional[date] = Field(None, description="Data fine prevista")
    sla_default_hours: Optional[int] = Field(48, ge=1, description="SLA default in ore")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadati aggiuntivi")

class CommessaCreate(CommessaBase):
    owner_id: Optional[UUID] = Field(None, description="ID owner (se non specificato, usa utente corrente)")

class CommessaUpdate(BaseModel):
    codice: Optional[str] = Field(None, min_length=1, max_length=50)
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    descrizione: Optional[str] = None
    client_id: Optional[int] = None
    owner_id: Optional[UUID] = None
    budget: Optional[float] = Field(None, ge=0)
    data_inizio: Optional[date] = None
    data_fine_prevista: Optional[date] = None
    status: Optional[str] = Field(None, pattern="^(active|paused|completed|closed)$")
    sla_default_hours: Optional[int] = Field(None, ge=1)
    metadata: Optional[Dict[str, Any]] = None

class CommessaResponse(CommessaBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    owner_id: Optional[UUID]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]

class CommessaListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    codice: str
    nome: str
    client_id: Optional[int]
    owner_id: Optional[UUID]
    status: str
    budget: Optional[float]
    data_inizio: Optional[date]
    data_fine_prevista: Optional[date]
    created_at: datetime

class CommessaDetailResponse(CommessaResponse):
    # TODO: Aggiungere milestone e tickets associati quando implementati
    milestones_count: Optional[int] = Field(0, description="Numero milestone associate")
    tickets_count: Optional[int] = Field(0, description="Numero ticket associati")
    tasks_count: Optional[int] = Field(0, description="Numero task associati")

class CommessaStats(BaseModel):
    total_budget: Optional[float]
    completed_percentage: Optional[float]
    overdue_tasks: int
    active_tickets: int
    team_members: int
