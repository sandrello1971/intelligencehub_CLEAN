"""
Intelligence AI Platform - Articles Model (ER Compatible)
Gestione articoli con nuovo schema ER
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, UUID, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Articolo(BaseModel):
    # Relationships
    partner = relationship("Partner", back_populates="articoli")
    __tablename__ = "articoli"
    
    # Campi originali (mantenuti per compatibilità)
    codice = Column(String(10), unique=True, nullable=False, index=True)
    nome = Column(String(200), nullable=False)
    descrizione = Column(Text)
    tipo_prodotto = Column(String(20), nullable=False)  # 'semplice' o 'composito'
    partner_id = Column(Integer, ForeignKey("partner.id"), nullable=True)
    attivo = Column(Boolean, default=True)
    
    # Nuovi campi ER
    art_code = Column(String(10))  # Mapping per ER
    art_description = Column(String(200))  # Mapping per ER  
    art_kit = Column(Boolean, default=False)  # true se è un kit
    
    # Campi di compatibilità
    tipo_commessa_legacy_id = Column(UUID)
    sla_default_hours = Column(Integer, default=48)
    template_milestones = Column(Text)
    
    def __repr__(self):
        return f"<Articolo {self.codice}: {self.nome} ({'Kit' if self.art_kit else 'Standard'})>"

    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            'id': self.id,
            'codice': self.codice,
            'nome': self.nome,
            'descrizione': self.descrizione,
            'tipo_prodotto': self.tipo_prodotto,
            'partner_id': self.partner_id,
            'attivo': self.attivo,
            # Campi ER
            'art_code': self.art_code or self.codice,
            'art_description': self.art_description or self.nome,
            'art_kit': self.art_kit,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
