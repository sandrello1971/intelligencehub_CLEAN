from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, ForeignKey, Numeric, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB
#from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base

class Commessa(Base):
    __tablename__ = "commesse"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codice = Column(String(50), unique=True, nullable=False, index=True)
    nome = Column(String(255), nullable=False)
    descrizione = Column(Text)
    client_id = Column(Integer, ForeignKey("companies.id"))
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    budget = Column(Numeric(15,2))
    data_inizio = Column(Date)
    data_fine_prevista = Column(Date)
    status = Column(String(50), default="active")
    sla_default_hours = Column(Integer, default=48)
    meta_data = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
#    client = relationship("Company", back_populates="commesse")
#    owner = relationship("User", back_populates="owned_commesse")
#    milestones = relationship("Milestone", back_populates="commessa")
#    tickets = relationship("Ticket", back_populates="commessa")
    
    def __repr__(self):
        return f"<Commessa {self.codice}: {self.nome}>"

class Milestone(Base):
    __tablename__ = "milestones"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    commessa_id = Column(UUID(as_uuid=True), ForeignKey("commesse.id"))
    nome = Column(String(255), nullable=False)
    descrizione = Column(Text)
    ordine = Column(Integer, nullable=False)
    sla_days = Column(Integer, default=7)
    warning_days = Column(Integer, default=2)
    escalation_days = Column(Integer, default=1)
    auto_generate_tickets = Column(Boolean, default=True)
    template_data = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
#    commessa = relationship("Commessa", back_populates="milestones")
#    tickets = relationship("Ticket", back_populates="milestone")
#    modelli_ticket = relationship("ModelloTicket", back_populates="milestone")

class ModelloTask(Base):
    __tablename__ = "modelli_task"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(255), nullable=False)
    descrizione = Column(Text)
    categoria = Column(String(100))
    sla_hours = Column(Integer, default=24)
    priorita = Column(String(50), default="medium")
    assignee_default_role = Column(String(50))
    checklist = Column(JSONB, default=[])
    template_content = Column(Text)
    tags = Column(JSONB, default=[])
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
#    created_by_user = relationship("User")
#    tasks = relationship("Task", back_populates="modello_task")

class ModelloTicket(Base):
    __tablename__ = "modelli_ticket"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(255), nullable=False)
    descrizione = Column(Text)
    milestone_id = Column(UUID(as_uuid=True), ForeignKey("milestones.id"))
    task_templates = Column(JSONB, default=[])  # Array di ModelloTask IDs
    auto_assign_rules = Column(JSONB, default={})
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
#    milestone = relationship("Milestone", back_populates="modelli_ticket")
