# models/tipi_commesse.py
# SQLAlchemy Models per Tipi Commesse - IntelligenceHUB

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float
from sqlalchemy.sql import func
from app.database import Base

class TipoCommessa(Base):
    """
    Modello per tipi di commesse configurabili
    """
    __tablename__ = "tipi_commesse"

    id = Column(String, primary_key=True, index=True)
    nome = Column(String(255), nullable=False, index=True)
    codice = Column(String(50), nullable=False, unique=True, index=True)
    descrizione = Column(Text, nullable=True)
    sla_default_hours = Column(Integer, nullable=False, default=48)
    
    # Template configurazione (JSON serializzato)
    template_milestones = Column(Text, nullable=True)  # JSON delle milestone template
    template_tasks = Column(Text, nullable=True)       # JSON dei task template
    
    # Stato e controllo
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Tracking modifiche
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    
    # Metadati aggiuntivi
    colore_ui = Column(String(7), nullable=True)  # Hex color per UI
    icona = Column(String(50), nullable=True)     # Nome icona Material-UI
    priorita_ordinamento = Column(Integer, default=0)  # Per ordinamento custom
    
    def __repr__(self):
        return f"<TipoCommessa(id={self.id}, codice={self.codice}, nome={self.nome})>"

class Milestone(Base):
    """
    Modello per milestone di progetto
    """
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    descrizione = Column(Text, nullable=True)
    
    # Riferimento a tipo commessa
    tipo_commessa_id = Column(String, nullable=True)  # FK verso tipi_commesse
    
    # Riferimento a opportunità/progetto
    
    # Date e tempistiche
    data_inizio = Column(DateTime(timezone=True), nullable=True)
    data_fine_prevista = Column(DateTime(timezone=True), nullable=True)
    data_fine_effettiva = Column(DateTime(timezone=True), nullable=True)
    
    # SLA e escalation
    sla_hours = Column(Integer, nullable=False, default=48)
    warning_days = Column(Integer, default=3)
    escalation_days = Column(Integer, default=7)
    
    # Automazione
    auto_generate_tickets = Column(Boolean, default=False)
    template_data = Column(Text, nullable=True)  # JSON configurazione automazione
    
    # Stato
    stato = Column(String(50), default="pianificata")  # pianificata, in_corso, completata, in_ritardo
    percentuale_completamento = Column(Float, default=0.0)
    
    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<Milestone(id={self.id}, nome={self.nome}, stato={self.stato})>"

class ModelloTask(Base):
    """
    Modello per template di task riutilizzabili
    """
    __tablename__ = "modelli_task"

    id = Column(String, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    descrizione = Column(Text, nullable=True)
    descrizione_operativa = Column(Text, nullable=True)  # Istruzioni dettagliate
    
    # SLA e priorità
    sla_hours = Column(Integer, nullable=False, default=24)
    priorita = Column(String(20), default="media")  # bassa, media, alta, critica
    
    # Ordinamento e raggruppamento
    ordine = Column(Integer, default=0)
    categoria = Column(String(100), nullable=True)
    tags = Column(String(500), nullable=True)  # Tags separati da virgola
    
    # Controllo workflow
    is_required = Column(Boolean, default=False)
    is_parallel = Column(Boolean, default=True)  # Può essere eseguito in parallelo
    dipendenze = Column(Text, nullable=True)  # JSON array di task dependencies
    
    # Associazione flessibile
    milestone_id = Column(Integer, nullable=True)      # FK verso milestones
    tipo_commessa_id = Column(String, nullable=True)   # FK verso tipi_commesse
    
    # Automazione
    auto_assign_logic = Column(Text, nullable=True)  # JSON logica assegnazione automatica
    notification_template = Column(Text, nullable=True)  # Template email notifications
    
    # Stato e controllo
    is_active = Column(Boolean, default=True)
    
    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<ModelloTask(id={self.id}, nome={self.nome}, sla_hours={self.sla_hours})>"
