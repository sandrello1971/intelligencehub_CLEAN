from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.sql import func

from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_log"
    
    # Schema esattamente come nel database
    id = Column(Integer, primary_key=True)  # NOT UUID - è INTEGER!
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String(100))
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    ip_address = Column(INET)
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=False), default=func.current_timestamp())
    
    def __repr__(self):
        return f"<AuditLog {self.action} by {self.user_id}>"
