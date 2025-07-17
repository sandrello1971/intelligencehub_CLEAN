# schemas/admin/tipi_commesse.py
# Pydantic schemas per Tipi Commesse - IntelligenceHUB

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime

class TipoCommessaBase(BaseModel):
    """Base schema per tipi commesse"""
    nome: str = Field(..., min_length=1, max_length=255, description="Nome del tipo commessa")
    codice: str = Field(..., min_length=1, max_length=50, description="Codice identificativo univoco")
    descrizione: Optional[str] = Field(None, description="Descrizione dettagliata")
    sla_default_hours: int = Field(48, ge=1, le=8760, description="SLA default in ore")
    is_active: bool = Field(True, description="Stato attivo/inattivo")
    
    # Configurazione UI
    colore_ui: Optional[str] = Field(None, regex=r'^#[0-9A-Fa-f]{6}$', description="Colore hex per UI")
    icona: Optional[str] = Field(None, max_length=50, description="Nome icona Material-UI")
    priorita_ordinamento: int = Field(0, description="Priorità per ordinamento")

    @validator('codice')
    def validate_codice(cls, v):
        """Valida e normalizza il codice"""
        if v:
            v = v.upper().strip()
            # Rimuovi caratteri non alfanumerici
            import re
            v = re.sub(r'[^A-Z0-9_]', '', v)
            if len(v) < 1:
                raise ValueError('Codice deve contenere almeno un carattere alfanumerico')
        return v

    @validator('nome')
    def validate_nome(cls, v):
        """Valida il nome"""
        if v:
            v = v.strip()
            if len(v) < 1:
                raise ValueError('Nome non può essere vuoto')
        return v

class TipoCommessaCreate(TipoCommessaBase):
    """Schema per creazione tipo commessa"""
    # Template configurazione opzionale
    template_milestones: Optional[Dict[str, Any]] = Field(None, description="Template milestone JSON")
    template_tasks: Optional[Dict[str, Any]] = Field(None, description="Template task JSON")

class TipoCommessaUpdate(BaseModel):
    """Schema per aggiornamento tipo commessa"""
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    codice: Optional[str] = Field(None, min_length=1, max_length=50)
    descrizione: Optional[str] = None
    sla_default_hours: Optional[int] = Field(None, ge=1, le=8760)
    is_active: Optional[bool] = None
    colore_ui: Optional[str] = Field(None, regex=r'^#[0-9A-Fa-f]{6}$')
    icona: Optional[str] = Field(None, max_length=50)
    priorita_ordinamento: Optional[int] = None
    template_milestones: Optional[Dict[str, Any]] = None
    template_tasks: Optional[Dict[str, Any]] = None

    @validator('codice')
    def validate_codice(cls, v):
        if v:
            v = v.upper().strip()
            import re
            v = re.sub(r'[^A-Z0-9_]', '', v)
            if len(v) < 1:
                raise ValueError('Codice deve contenere almeno un carattere alfanumerico')
        return v

    @validator('nome')
    def validate_nome(cls, v):
        if v:
            v = v.strip()
            if len(v) < 1:
                raise ValueError('Nome non può essere vuoto')
        return v

class TipoCommessa(TipoCommessaBase):
    """Schema per lettura tipo commessa"""
    id: str
    template_milestones: Optional[Dict[str, Any]] = None
    template_tasks: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        orm_mode = True

class TipoCommessaInDB(TipoCommessa):
    """Schema completo per database"""
    pass

# Response schemas
class TipoCommessaResponse(BaseModel):
    """Schema per risposte API"""
    success: bool = True
    data: Optional[TipoCommessa] = None
    message: Optional[str] = None
    error: Optional[str] = None

class TipoCommessaListResponse(BaseModel):
    """Schema per liste paginate"""
    success: bool = True
    data: list[TipoCommessa] = []
    total: int = 0
    page: int = 1
    per_page: int = 20
    total_pages: int = 0
    has_next: bool = False
    has_prev: bool = False
