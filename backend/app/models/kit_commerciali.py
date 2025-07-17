"""
Intelligence AI Platform - Kit Commerciali Models
Gestione kit commerciali e associazioni articoli
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DECIMAL, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class KitCommerciale(Base):
    __tablename__ = "kit_commerciali"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False)
    descrizione = Column(Text)
    articolo_principale_id = Column(Integer, ForeignKey("articoli.id"))
    attivo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())  # Solo created_at come nel DB
    
    # Relationships
    articolo_principale = relationship("Articolo", backref="kit_principale")
    kit_articoli = relationship("KitArticolo", back_populates="kit_commerciale", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<KitCommerciale {self.nome}>"

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descrizione': self.descrizione,
            'articolo_principale_id': self.articolo_principale_id,
            'articolo_principale': self.articolo_principale.to_dict() if self.articolo_principale else None,
            'attivo': self.attivo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'articoli_inclusi': [ka.to_dict() for ka in self.kit_articoli] if self.kit_articoli else [],
            'articoli_count': len(self.kit_articoli) if self.kit_articoli else 0
        }

class KitArticolo(Base):
    __tablename__ = "kit_articoli"
    
    id = Column(Integer, primary_key=True, index=True)
    kit_commerciale_id = Column(Integer, ForeignKey("kit_commerciali.id"), nullable=False)
    articolo_id = Column(Integer, ForeignKey("articoli.id"), nullable=False)
    quantita = Column(Integer, default=1)
    obbligatorio = Column(Boolean, default=False)
    ordine = Column(Integer, default=0)
    
    # Relationships
    kit_commerciale = relationship("KitCommerciale", back_populates="kit_articoli")
    articolo = relationship("Articolo", backref="kit_articoli_rel")
    
    def __repr__(self):
        return f"<KitArticolo Kit:{self.kit_commerciale_id} Art:{self.articolo_id}>"

    def to_dict(self):
        return {
            'id': self.id,
            'kit_commerciale_id': self.kit_commerciale_id,
            'articolo_id': self.articolo_id,
            'articolo': self.articolo.to_dict() if self.articolo else None,
            'quantita': self.quantita,
            'obbligatorio': self.obbligatorio,
            'ordine': self.ordine
        }
