from sqlalchemy import Column, String, ForeignKey, DateTime, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base
import uuid


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(String(500))

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    company_id = Column(BigInteger, ForeignKey("companies.id"))

    created_at = Column(DateTime)

    # Relazioni
#    creator = relationship("User", back_populates="created_tickets", foreign_keys=[created_by])
#    assigned_user = relationship("User", back_populates="assigned_tickets", foreign_keys=[assigned_to])
#    company = relationship("Company", back_populates="tickets")

    # Relazioni verso User (User è già definito quando Ticket viene caricato)
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_tickets")
    assigned_user = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_tickets")
    company = relationship("Company")
