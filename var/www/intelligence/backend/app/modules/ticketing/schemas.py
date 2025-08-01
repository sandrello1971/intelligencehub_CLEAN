"""
Intelligence Ticketing Module - Schemas
Pydantic models for API validation and serialization
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ===== TASK SCHEMAS =====

class TaskBase(BaseModel):
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    status: Optional[str] = Field("pending", description="Task status")
    priority: Optional[str] = Field("medium", description="Task priority")
    owner: Optional[str] = Field(None, description="Task owner ID")
    predecessor_id: Optional[int] = Field(None, description="Predecessor task ID")
    parent_id: Optional[int] = Field(None, description="Parent task ID")

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    owner: Optional[str] = None
    note: Optional[str] = None
    responsabile_name: Optional[str] = None
    responsabile_id: Optional[str] = None
    articolo_nome: Optional[str] = None
    predecessor_id: Optional[int] = None
    parent_id: Optional[int] = None
    services: Optional[List[str]] = None

class TaskResponse(BaseModel):
    id: str
    ticket_id: str
    ticket_code: Optional[str]
    title: str
    description: Optional[str]
    status: str
    priority: str
    owner: Optional[str]
    owner_name: Optional[str]
    due_date: Optional[datetime]
    predecessor_id: Optional[int]
    predecessor_title: Optional[str]
    closed_at: Optional[datetime]
    note: Optional[str]
    responsabile_name: Optional[str] = None
    responsabile_id: Optional[str] = None
    articolo_nome: Optional[str] = None
    siblings: List[Dict[str, Any]]
    
    class Config:
        from_attributes = True

class TaskListItem(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: str
    priority: str
    ticket_id: str
    owner: Optional[str]
    predecessor_id: Optional[int]
    milestone_id: Optional[int]
    closed_at: Optional[datetime]
    note: Optional[str]
    responsabile_name: Optional[str] = None
    responsabile_id: Optional[str] = None
    articolo_nome: Optional[str] = None
    
    class Config:
        from_attributes = True


# ===== TICKET SCHEMAS =====

class TicketBase(BaseModel):
    title: str = Field(..., description="Ticket title")
    description: Optional[str] = Field(None, description="Ticket description")
    priority: Optional[int] = Field(1, description="Ticket priority (0=low, 1=medium, 2=high)")
    customer_name: Optional[str] = Field(None, description="Customer name")
    gtd_type: Optional[int] = Field(None, description="GTD type")

class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    status: Optional[int] = None
    customer_name: Optional[str] = None
    owner: Optional[str] = None
    note: Optional[str] = None
    responsabile_name: Optional[str] = None
    responsabile_id: Optional[str] = None
    articolo_nome: Optional[str] = None

class TicketResponse(BaseModel):
    id: str
    ticket_code: Optional[str]
    title: str
    description: Optional[str]
    priority: int
    status: int
    due_date: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    owner_id: Optional[int]
    gtd_type: Optional[int]
    assigned_to: Optional[int]
    owner: Optional[str]
    account: Optional[str]
    milestone_id: Optional[int]
    customer_name: Optional[str]
    gtd_generated: Optional[bool]
    detected_services: Optional[List[str]]
    activity: Optional[Dict[str, Any]]
    tasks: List[Dict[str, Any]]
    tasks_stats: Dict[str, int]
    
    class Config:
        from_attributes = True

class TicketListItem(BaseModel):
    id: str  # UUID come stringa
    ticket_code: Optional[str]
    title: Optional[str]
    description: Optional[str]
    priority: Optional[str]  # Stringa, non int
    status: Optional[str]  # Stringa, non int
    due_date: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: Optional[str]  # UUID come stringa
    assigned_to: Optional[str]  # UUID come stringa
    company_id: Optional[int]
    milestone_id: Optional[str]  # UUID come stringa
    tasks: Optional[List[Dict]] = []
    tasks_stats: Optional[Dict] = {}
    
    class Config:
        from_attributes = True

# ===== UTILITY SCHEMAS =====

class ServicesInput(BaseModel):
    services: List[str] = Field(..., description="List of services")

class TicketFilters(BaseModel):
    priority: Optional[str] = None
    status: Optional[str] = None
    customer_name: Optional[str] = None

class TaskFilters(BaseModel):
    status: Optional[str] = None
    owner: Optional[str] = None
    note: Optional[str] = None
    responsabile_name: Optional[str] = None
    responsabile_id: Optional[str] = None
    articolo_nome: Optional[str] = None
    priority: Optional[str] = None

class BulkOperationResult(BaseModel):
    tickets_closed: int
    closed_ids: List[int]
    timestamp: str

# ===== COMMERCIAL SCHEMAS =====

class CommercialCommessaRequest(BaseModel):
    """Schema per creazione commessa da kit commerciale"""
    company_id: str = Field(..., description="ID azienda dal database")
    kit_commerciale_id: str = Field(..., description="ID kit commerciale")
    notes: Optional[str] = Field("", description="Note aggiuntive")
    owner_id: Optional[str] = Field(None, description="Owner, default utente corrente")

class CommercialCommessaResponse(BaseModel):
    """Schema risposta creazione commessa commerciale"""
    success: bool
    commessa_id: str
    ticket_padre: TicketResponse
    kit_info: Dict[str, Any]
    servizi_inclusi: List[str]
    crm_activity_id: Optional[int] = None
    milestones_generate: List[Dict[str, Any]]
    message: str

class OpportunityGenerationRequest(BaseModel):
    """Schema per generazione opportunità/ticket figli"""
    commessa_id: str = Field(..., description="ID commessa padre")
    force_generation: bool = Field(False, description="Forza anche se task aperti")

class OpportunityGenerationResponse(BaseModel):
    """Schema risposta generazione opportunità"""
    success: bool
    commessa_id: str
    opportunita_create: List[Dict[str, Any]]
    ticket_figli_generati: List[TicketResponse]
    message: str

