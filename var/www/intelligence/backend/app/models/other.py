from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
#from sqlalchemy.orm import relationship
from .base import Base

class SubType(Base):
    __tablename__ = "sub_types"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False)
    
    # Relationships
    #activities = relationship("Activity", back_populates="subtype")

class Owner(Base):
    __tablename__ = "owners"
    
    id = Column(String, primary_key=True)
    name = Column(String)
    surname = Column(String)
    email = Column(String)

class PhaseTemplate(Base):
    __tablename__ = "phase_templates"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, nullable=False)
    type = Column(String, nullable=False)
    description = Column(String, nullable=False)
    milestone_id = Column(Integer, ForeignKey("milestones.id"))
    order = Column(Integer)
    parent_id = Column(Integer, ForeignKey("phase_templates.id"))

class Opportunity(Base):
    __tablename__ = "opportunities"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    titolo = Column(String)
    cliente = Column(String)
    descrizione = Column(String)
    stato = Column(String)
    fase = Column(String)
    probabilita = Column(String)
    data_chiusura = Column(String)
    data_creazione = Column(String)
    data_modifica = Column(String)
    proprietario = Column(String)
    commerciale = Column(String)
    codice = Column(String)
    categoria = Column(String)
    ammontare = Column(String)

class CrmLink(Base):
    __tablename__ = "crm_links"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    local_ticket_id = Column(Integer, ForeignKey("tickets.id"))
    crm_activity_id = Column(Integer)
    crm_company_id = Column(Integer)
    created_at = Column(DateTime)
    
    # Relationships
    #ticket = relationship("Ticket", back_populates="crm_links")

# ✅ Import ritardato per risolvere relazione circolare
import app.models.activity
