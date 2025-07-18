from sqlalchemy import Column, String, ForeignKey, DateTime, BigInteger, Integer, Boolean, Text, Date, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base_class import Base
import uuid

class Task(Base):
    __tablename__ = "tasks"

    # Campi base
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"))
    milestone_id = Column(UUID(as_uuid=True), ForeignKey("milestones.id"))
    title = Column(Text)
    description = Column(Text)
    status = Column(Text, default='todo')
    due_date = Column(Date)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, server_default='now()')
    
    # Template e modelli
    modello_task_id = Column(UUID(as_uuid=True), ForeignKey("modelli_task.id"))
    
    # SLA - CAMPI PRINCIPALI
    sla_hours = Column(Integer, default=24)
    sla_deadline = Column(DateTime)
    
    # SLA - NUOVI CAMPI A 3 LIVELLI  
    sla_giorni = Column(Integer)
    warning_giorni = Column(Integer, default=1)
    escalation_giorni = Column(Integer, default=1)
    warning_deadline = Column(DateTime)
    escalation_deadline = Column(DateTime)
    
    # Ore stimate/effettive
    estimated_hours = Column(Numeric(5,2))
    actual_hours = Column(Numeric(5,2))
    
    # Metadata
    checklist = Column(JSONB, default=[])
    task_task_metadata = Column(JSONB, default={})
    

    class Config:
        from_attributes = True
