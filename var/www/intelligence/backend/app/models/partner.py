"""
Intelligence AI Platform - Partner Model
Gestione partner commerciali e fornitori
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import BaseModel

class Partner(BaseModel):
    __tablename__ = "partner"
    
    nome = Column(String(200), nullable=False)
    ragione_sociale = Column(String(250))
    partita_iva = Column(String(20))
    email = Column(String(100))
    telefono = Column(String(50))
    sito_web = Column(String(200))
    indirizzo = Column(Text)
    note = Column(Text)
    attivo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    articoli = relationship("Articolo", back_populates="partner")
    
    def __repr__(self):
        return f"<Partner {self.nome}>"
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            'id': self.id,
            'nome': self.nome,
            'ragione_sociale': self.ragione_sociale,
            'partita_iva': self.partita_iva,
            'email': self.email,
            'telefono': self.telefono,
            'sito_web': self.sito_web,
            'indirizzo': self.indirizzo,
            'note': self.note,
            'attivo': self.attivo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
