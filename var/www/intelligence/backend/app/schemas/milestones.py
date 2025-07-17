from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

class MilestoneBase(BaseModel):
    titolo: str = Field(..., min_length=1, max_length=200)
    descrizione: Optional[str] = None
    commessa_id: int
    data_scadenza: Optional[datetime] = None
    budget: Optional[Decimal] = None
    status: str = Field(default="planned", pattern="^(planned|in_progress|completed|cancelled)$")

class MilestoneCreate(MilestoneBase):
    pass

class MilestoneUpdate(BaseModel):
    titolo: Optional[str] = Field(None, min_length=1, max_length=200)
    descrizione: Optional[str] = None
    data_scadenza: Optional[datetime] = None
    budget: Optional[Decimal] = None
    status: Optional[str] = Field(None, pattern="^(planned|in_progress|completed|cancelled)$")

class MilestoneResponse(MilestoneBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Classe mancante per lista milestone
class MilestoneListItem(BaseModel):
    id: int
    titolo: str
    commessa_id: int
    status: str
    data_scadenza: Optional[datetime] = None
    budget: Optional[Decimal] = None
    
    class Config:
        from_attributes = True

# Classe per dettaglio milestone
class MilestoneDetailResponse(MilestoneResponse):
    # Eredita tutto da MilestoneResponse, aggiunge dettagli se necessario
    pass
