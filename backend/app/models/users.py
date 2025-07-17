from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    # Colonne esattamente come nel database
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(Text, unique=True, nullable=False, index=True)
    email = Column(Text, unique=True, nullable=False, index=True)
    password_hash = Column(Text)
    role = Column(Text, nullable=False, default="operator")
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    name = Column(Text)
    surname = Column(Text)
    first_name = Column(String(100))
    last_name = Column(String(100))
    permissions = Column(JSONB, default=dict)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=False))
    must_change_password = Column(Boolean, default=False)
    crm_id = Column(Integer)
    
    def __repr__(self):
        return f"<User {self.username}>"
    
    def get_assigned_tickets(self, db):
        """Ottieni tutti i ticket assegnati a questo utente"""
        pass
    
    def get_created_tickets(self, db):
        """Ottieni tutti i ticket creati da questo utente"""
        pass
    
    def get_assigned_tasks(self, db):
        """Ottieni tutti i task assegnati a questo utente"""
        pass

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    permissions = Column(JSONB, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    
    def __repr__(self):
        return f"<Role {self.name}>"
