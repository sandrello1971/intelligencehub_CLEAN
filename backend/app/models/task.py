from sqlalchemy import Column, String, ForeignKey, DateTime, BigInteger
from sqlalchemy.dialects.postgresql import UUID
#from sqlalchemy.orm import relationship
from app.db.base_class import Base
import uuid


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(String(500))

    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    company_id = Column(BigInteger, ForeignKey("companies.id"))

    created_at = Column(DateTime)
    due_date = Column(DateTime)

    # Relazioni
#    assigned_user = relationship("User", back_populates="assigned_tasks")
#    company = relationship("Company", back_populates="tasks")
