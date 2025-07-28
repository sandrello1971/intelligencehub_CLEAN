from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, ForeignKey, Numeric, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class Commessa(Base):
    __tablename__ = "commesse"
    
    # Campi reali dal database
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(Integer, ForeignKey("companies.id"))
    name = Column(Text, nullable=False)  # Nome della commessa
    codice = Column(Text)
    descrizione = Column(Text)
    stato = Column(Text, default='attiva')
    created_at = Column(DateTime, default=func.now())
    client_id = Column(Integer, ForeignKey("companies.id"))
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    budget = Column(Numeric(15,2))
    data_inizio = Column(Date)
    data_fine_prevista = Column(Date)
    status = Column(String(50), default='active')
    sla_default_hours = Column(Integer, default=48)
    meta_data = Column("metadata", JSONB, default=dict)
    updated_at = Column(DateTime, default=func.now())
    kit_commerciale_id = Column(Integer, ForeignKey("kit_commerciali.id"))
    commerciale_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    tipo_commessa = Column(String(50), default='standard')
    valore_contratto = Column(Numeric(15,2))
    ord_date = Column(Date)
    ord_description = Column(Text)
    cst_id = Column(Integer)
    
    # Proprietà per compatibilità con il codice esistente
    @property
    def nome(self):
        return self.name
    
    @nome.setter
    def nome(self, value):
        self.name = value
    
    def __repr__(self):
        return f"<Commessa {self.codice}: {self.name}>"

