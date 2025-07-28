"""
Company model - Minimal mapping for existing database
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, Date, DateTime
from sqlalchemy.dialects.postgresql import BIGINT, JSONB
from sqlalchemy.sql import func
from app.core.database import Base

class Company(Base):
    __tablename__ = "companies"
    
    # Solo i campi essenziali che sicuramente esistono
    id = Column(BIGINT, primary_key=True, index=True)
    name = Column(Text, nullable=False)
    partita_iva = Column(Text)
    codice_fiscale = Column(Text)
    indirizzo = Column(Text)
    settore = Column(Text)
    email = Column(Text)
    telefono = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    # Proprietà per compatibilità con il codice esistente
    @property
    def nome(self):
        return self.name
    
    def __repr__(self):
        return f"<Company {self.name}>"

