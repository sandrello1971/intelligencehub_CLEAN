"""
Intelligence AI Platform - ER Models
Nuovi modelli per schema ER
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, UUID, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class TaskGlobal(Base):
    __tablename__ = "tasks_global"
    
    id = Column(Integer, primary_key=True, index=True)
    tsk_code = Column(String(50), nullable=False, unique=True)
    tsk_description = Column(Text)
    tsk_type = Column(String(20), default='standard')
    tsk_category = Column(String(50))
    sla_giorni = Column(Integer)
    warning_giorni = Column(Integer, default=1)
    escalation_giorni = Column(Integer, default=1)
    priorita = Column(String(20), default="normale")
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<TaskGlobal {self.tsk_code}: {self.tsk_description}>"

    def to_dict(self):
        return {
            'id': self.id,
            'tsk_code': self.tsk_code,
            'tsk_description': self.tsk_description,
            'tsk_type': self.tsk_type,
            'tsk_category': self.tsk_category,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sla_giorni': self.sla_giorni,
            'warning_giorni': self.warning_giorni,
            'escalation_giorni': self.escalation_giorni,
            'priorita': self.priorita
        }

class WkfRow(Base):
    __tablename__ = "wkf_rows"
    
    id = Column(Integer, primary_key=True, index=True)
    wkf_id = Column(Integer)  # Rimuovo FK temporaneamente
    tsk_id = Column(Integer, ForeignKey("tasks_global.id"))
    mls_id = Column(Integer)  # Rimuovo FK temporaneamente
    tsk_position = Column(String(20), default='middle')
    tsk_sla_hours = Column(Integer, default=24)
    tsk_order = Column(Integer, default=0)
    tsk_mandatory = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships solo con TaskGlobal per ora
    task = relationship("TaskGlobal", backref="wkf_rows")
    
    def __repr__(self):
        return f"<WkfRow WKF:{self.wkf_id} TSK:{self.tsk_id}>"

    def to_dict(self):
        return {
            'id': self.id,
            'wkf_id': self.wkf_id,
            'tsk_id': self.tsk_id,
            'mls_id': self.mls_id,
            'tsk_position': self.tsk_position,
            'tsk_sla_hours': self.tsk_sla_hours,
            'tsk_order': self.tsk_order,
            'tsk_mandatory': self.tsk_mandatory,
            'task': self.task.to_dict() if self.task else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class TicketRow(Base):
    __tablename__ = "ticket_rows"
    
    id = Column(Integer, primary_key=True, index=True)
    tck_id = Column(UUID)  # Rimuovo FK temporaneamente
    tsk_id = Column(Integer, ForeignKey("tasks_global.id"))
    wkf_row_id = Column(Integer, ForeignKey("wkf_rows.id"))
    tsk_status = Column(String(20), default='todo')
    tsk_assigned_to = Column(UUID)  # Rimuovo FK temporaneamente
    tsk_start_date = Column(DateTime)
    tsk_due_date = Column(DateTime)
    tsk_completed_date = Column(DateTime)
    tsk_notes = Column(Text)
    tsk_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    task = relationship("TaskGlobal", backref="ticket_rows")
    wkf_row = relationship("WkfRow", backref="ticket_rows")
    
    def __repr__(self):
        return f"<TicketRow TCK:{self.tck_id} TSK:{self.tsk_id}>"

    def to_dict(self):
        return {
            'id': self.id,
            'tck_id': str(self.tck_id) if self.tck_id else None,
            'tsk_id': self.tsk_id,
            'wkf_row_id': self.wkf_row_id,
            'tsk_status': self.tsk_status,
            'tsk_assigned_to': str(self.tsk_assigned_to) if self.tsk_assigned_to else None,
            'tsk_start_date': self.tsk_start_date.isoformat() if self.tsk_start_date else None,
            'tsk_due_date': self.tsk_due_date.isoformat() if self.tsk_due_date else None,
            'tsk_completed_date': self.tsk_completed_date.isoformat() if self.tsk_completed_date else None,
            'tsk_notes': self.tsk_notes,
            'tsk_order': self.tsk_order,
            'task': self.task.to_dict() if self.task else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
