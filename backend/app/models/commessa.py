from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
#from sqlalchemy.orm import relationship
from app.db.base_class import Base
import uuid


class Commessa(Base):
    __tablename__ = "commesse"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

#    owner = relationship("User", back_populates="owned_commesse", foreign_keys=[owner_id])
