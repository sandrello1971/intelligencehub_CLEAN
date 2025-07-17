from sqlalchemy import Integer, Column, String, ForeignKey, DateTime, BigInteger
from sqlalchemy.dialects.postgresql import UUID
#from sqlalchemy.orm import relationship
from app.db.base_class import Base
import uuid

class Activity(Base):
    __tablename__ = "activities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    company_id = Column(BigInteger, ForeignKey("companies.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    subtype_id = Column(Integer, ForeignKey("sub_types.id"))
    created_at = Column(DateTime)
    
    # Relazioni con string references per evitare import circolari
    #subtype = relationship("SubType", back_populates="activities")
    #company = relationship("Company", back_populates="activities")
    #user = relationship("User", back_populates="activities")
