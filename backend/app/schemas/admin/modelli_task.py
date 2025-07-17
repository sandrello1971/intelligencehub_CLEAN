# schemas/admin/modelli_task.py
# Pydantic schemas per Modelli Task - IntelligenceHUB

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime

class ModelloTaskBase(BaseModel):
    """Base schema per modelli task"""
    nome: str = Field(..., min_length=1, max_length=255, description="Nome template task")
    descrizione: Optional[str] = Field(None, description="Descrizione task")
    descrizione_operativa: Optional[str] = Field(None, description="Istruzioni operative dettagliate")
    
    # SLA e priorità
    sla_hours: int = Field(24, ge=1, le=8760, description="SLA in ore")
    priorita: str = Field("media", description="Priorità task")
    
    # Organizzazione
    ordine: int = Field(0, description="Ordine di esecuzione")
    categoria: Optional[str] = Field(None, max_length=100, description="Categoria task")
    tags: Optional[str] = Field(None, max_length=500, description="Tags separati da virgola")
    
    # Controllo workflow
    is_required: bool = Field(False, description="Task obbligatorio")
    is_parallel: bool = Field(True, description="Eseguibile in parallelo")
    dipendenze: Optional[List[str]] = Field(None, description="Lista dipendenze task")
    
    # Associazione
    milestone_id: Optional[int] = Field(None, description="ID milestone")
    tipo_commessa_id: Optional[str] = Field(None, description="ID tipo commessa")
    
    # Automazione
    auto_assign_logic: Optional[Dict[str, Any]] = Field(None, description="Logica assegnazione automatica")
    notification_template: Optional[Dict[str, Any]] = Field(None, description="Template notifiche")
    
    # Stato
    is_active: bool = Field(True, description="Template attivo")

    @validator('nome')
    def validate_nome(cls, v):
        if v:
            v = v.strip()
            if len(v) < 1:
                raise ValueError('Nome template non può essere vuoto')
        return v

    @validator('priorita')
    def validate_priorita(cls, v):
        valid_priorita = ['bassa', 'media', 'alta', 'critica']
        if v not in valid_priorita:
            raise ValueError(f'Priorità deve essere una di: {", ".join(valid_priorita)}')
        return v

    @validator('tags')
    def validate_tags(cls, v):
        if v:
            # Normalizza tags: lowercase, rimuovi spazi extra
            tags = [tag.strip().lower() for tag in v.split(',') if tag.strip()]
            return ', '.join(tags)
        return v

class ModelloTaskCreate(ModelloTaskBase):
    """Schema per creazione modello task"""
    pass

class ModelloTaskUpdate(BaseModel):
    """Schema per aggiornamento modello task"""
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    descrizione: Optional[str] = None
    descrizione_operativa: Optional[str] = None
    sla_hours: Optional[int] = Field(None, ge=1, le=8760)
    priorita: Optional[str] = None
    ordine: Optional[int] = None
    categoria: Optional[str] = Field(None, max_length=100)
    tags: Optional[str] = Field(None, max_length=500)
    is_required: Optional[bool] = None
    is_parallel: Optional[bool] = None
    dipendenze: Optional[List[str]] = None
    milestone_id: Optional[int] = None
    tipo_commessa_id: Optional[str] = None
    auto_assign_logic: Optional[Dict[str, Any]] = None
    notification_template: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

    @validator('nome')
    def validate_nome(cls, v):
        if v:
            v = v.strip()
            if len(v) < 1:
                raise ValueError('Nome template non può essere vuoto')
        return v

    @validator('priorita')
    def validate_priorita(cls, v):
        if v:
            valid_priorita = ['bassa', 'media', 'alta', 'critica']
            if v not in valid_priorita:
                raise ValueError(f'Priorità deve essere una di: {", ".join(valid_priorita)}')
        return v

    @validator('tags')
    def validate_tags(cls, v):
        if v:
            tags = [tag.strip().lower() for tag in v.split(',') if tag.strip()]
            return ', '.join(tags)
        return v

class ModelloTask(ModelloTaskBase):
    """Schema per lettura modello task"""
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        orm_mode = True

class ModelloTaskInDB(ModelloTask):
    """Schema completo per database"""
    pass

# Utility schemas
class TaskAssignmentRule(BaseModel):
    """Schema per regole di assegnazione automatica"""
    condition: str = Field(..., description="Condizione per l'assegnazione")
    user_id: Optional[str] = Field(None, description="ID utente target")
    role: Optional[str] = Field(None, description="Ruolo target")
    skill_required: Optional[str] = Field(None, description="Skill richiesta")

class NotificationRule(BaseModel):
    """Schema per regole di notifica"""
    trigger: str = Field(..., description="Trigger notifica")
    template: str = Field(..., description="Template messaggio")
    recipients: List[str] = Field(..., description="Lista destinatari")
    delay_hours: int = Field(0, description="Ritardo in ore")
