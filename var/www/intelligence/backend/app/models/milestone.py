from app.db.base_class import Base
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Milestone(Base):
    __tablename__ = "milestones"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
