from sqlalchemy import Column, String, ForeignKey, DateTime, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base
import uuid


class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(BigInteger, ForeignKey("companies.id"))
    title = Column(String)
    description = Column(String)
    status = Column(String)
    priority = Column(String)
    created_at = Column(DateTime)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    opportunity_id = Column(UUID(as_uuid=True))
    modello_ticket_id = Column(UUID(as_uuid=True))
    milestone_id = Column(UUID(as_uuid=True))
    sla_deadline = Column(DateTime)
    ticket_ticket_metadata = Column("metadata", String)  # JSONB in PostgreSQL
    commessa_id = Column(UUID(as_uuid=True))
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    activity_id = Column(BigInteger)
    articolo_id = Column(BigInteger)
    workflow_milestone_id = Column(BigInteger)
    ticket_code = Column(String(50))
    due_date = Column(DateTime)
    updated_at = Column(DateTime)
