from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class WorkflowTemplate(Base):
    __tablename__ = "workflow_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False)
    descrizione = Column(Text)
    durata_stimata_giorni = Column(Integer)
    ordine = Column(Integer, default=0)
    attivo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    wkf_code = Column(String(50))
    wkf_description = Column(Text)
