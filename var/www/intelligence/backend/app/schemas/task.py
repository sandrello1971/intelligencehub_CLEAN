from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID

class TaskSLABase(BaseModel):
    """Schema base per SLA tasks"""
    sla_giorni: Optional[int] = Field(None, ge=1, le=365, description="SLA totale in giorni")
    warning_giorni: int = Field(1, ge=0, le=30, description="Giorni warning prima scadenza")
    escalation_giorni: int = Field(1, ge=0, le=30, description="Giorni escalation dopo scadenza")

class TaskSLAResponse(TaskSLABase):
    """Schema risposta con deadline calcolate"""
    sla_deadline: Optional[datetime] = None
    description: Optional[str]
    sla_giorni: Optional[int]
    warning_giorni: Optional[int]
    escalation_giorni: Optional[int]
    warning_deadline: Optional[datetime]
    escalation_deadline: Optional[datetime]
    warning_deadline: Optional[datetime] = None
    escalation_deadline: Optional[datetime] = None
    
    @property
    def sla_status(self) -> str:
        """Calcola stato SLA attuale"""
        if not self.sla_deadline:
            return "NO_SLA"
        
        now = datetime.utcnow()
        if now < self.warning_deadline:
            return "GREEN"
        elif now <= self.sla_deadline:
            return "YELLOW"
        elif now <= self.escalation_deadline:
            return "ORANGE"
        else:
            return "RED"

class TaskCreate(BaseModel):
    """Schema creazione task"""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    ticket_id: Optional[UUID] = None
    milestone_id: Optional[UUID] = None
    assigned_to: Optional[UUID] = None
    due_date: Optional[date] = None
    
    # SLA configurabili
    sla_giorni: Optional[int] = Field(None, ge=1, le=365)
    warning_giorni: int = Field(1, ge=0, le=30)
    escalation_giorni: int = Field(1, ge=0, le=30)
    
    # SLA manuali (opzionali)
    sla_deadline: Optional[datetime] = None
    description: Optional[str]
    sla_giorni: Optional[int]
    warning_giorni: Optional[int]
    escalation_giorni: Optional[int]
    warning_deadline: Optional[datetime]
    escalation_deadline: Optional[datetime]
    warning_deadline: Optional[datetime] = None
    escalation_deadline: Optional[datetime] = None
    
    # Altri campi
    priorita: str = Field("normale", pattern="^(bassa|normale|alta|critica)$")
    estimated_hours: Optional[float] = Field(None, ge=0, le=999.99)
    checklist: List[Dict[str, Any]] = Field(default=[])
    task_metadata: Dict[str, Any] = Field(default={})

class TaskUpdate(BaseModel):
    """Schema aggiornamento task"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(todo|in_progress|completed|cancelled)$")
    assigned_to: Optional[UUID] = None
    due_date: Optional[date] = None
    
    # Aggiornamento SLA
    sla_giorni: Optional[int] = Field(None, ge=1, le=365)
    warning_giorni: Optional[int] = Field(None, ge=0, le=30)
    escalation_giorni: Optional[int] = Field(None, ge=0, le=30)
    
    # SLA manuali
    sla_deadline: Optional[datetime] = None
    description: Optional[str]
    sla_giorni: Optional[int]
    warning_giorni: Optional[int]
    escalation_giorni: Optional[int]
    warning_deadline: Optional[datetime]
    escalation_deadline: Optional[datetime]
    warning_deadline: Optional[datetime] = None
    escalation_deadline: Optional[datetime] = None
    
    # Altri campi
    priorita: Optional[str] = Field(None, pattern="^(bassa|normale|alta|critica)$")
    estimated_hours: Optional[float] = Field(None, ge=0, le=999.99)
    actual_hours: Optional[float] = Field(None, ge=0, le=999.99)
    checklist: Optional[List[Dict[str, Any]]] = None
    task_metadata: Optional[Dict[str, Any]] = None

class TaskResponse(TaskSLAResponse):
    """Schema risposta completa task"""
    id: UUID
    title: str
    description: Optional[str]
    status: str
    ticket_id: Optional[UUID]
    milestone_id: Optional[UUID]
    assigned_to: Optional[UUID]
    due_date: Optional[date]
    created_at: datetime
    
    # SLA completi (ereditati da TaskSLAResponse)
    
    # Altri campi
    priorita: str
    estimated_hours: Optional[float]
    actual_hours: Optional[float]
    checklist: List[Dict[str, Any]]
    task_metadata: Dict[str, Any]
    
    # Campi relazionali
    parent_task_id: Optional[UUID] = None
    company_id: Optional[int] = None
    commessa_id: Optional[UUID] = None
    
    class Config:
        from_attributes = True

class TaskListItem(BaseModel):
    """Schema per lista tasks (versione leggera)"""
    id: UUID
    title: str
    status: str
    assigned_to: Optional[UUID]
    sla_deadline: Optional[datetime]
    description: Optional[str]
    sla_giorni: Optional[int]
    warning_giorni: Optional[int]
    escalation_giorni: Optional[int]
    warning_deadline: Optional[datetime]
    escalation_deadline: Optional[datetime]
    sla_status: str  # GREEN, YELLOW, ORANGE, RED
    priorita: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class TaskSLAMonitoring(BaseModel):
    """Schema per monitoring SLA"""
    green_tasks: int = Field(..., description="Task nei tempi")
    yellow_tasks: int = Field(..., description="Task in scadenza")
    orange_tasks: int = Field(..., description="Task scaduti")
    red_tasks: int = Field(..., description="Task molto in ritardo")
    
    green_list: List[TaskListItem] = []
    yellow_list: List[TaskListItem] = []
    orange_list: List[TaskListItem] = []
    red_list: List[TaskListItem] = []
