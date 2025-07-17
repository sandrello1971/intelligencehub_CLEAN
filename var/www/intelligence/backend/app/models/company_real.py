"""
Intelligence AI Platform - Company Model (Real Structure)
Based on actual database schema with partner extensions
"""

from sqlalchemy import Column, BigInteger, String, Text, Integer, Date, Float, Boolean, DateTime, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.db.base_class import Base

class Company(Base):
    """Company model based on real database structure"""
    __tablename__ = "companies"
    
    # Existing fields (from real DB)
    id = Column(BigInteger, primary_key=True)
    codice = Column(Text)
    name = Column(Text, nullable=False)
    partita_iva = Column(Text, index=True)
    codice_fiscale = Column(Text)
    indirizzo = Column(Text)
    citta = Column(Text)
    cap = Column(Text)
    provincia = Column(Text)
    regione = Column(Text)
    stato = Column(Text, default='IT')
    settore = Column(Text, index=True)
    numero_dipendenti = Column(Integer)
    data_acquisizione = Column(Date)
    note = Column(Text)
    sito_web = Column(Text, index=True)
    email = Column(Text)
    telefono = Column(Text)
    score = Column(Integer)
    zona_commerciale = Column(Text)
    sales_persons = Column(JSONB)
    created_at = Column(DateTime, server_default=func.now())
    
    # NEW: Partner/Supplier fields (to be added by migration)
    is_partner = Column(Boolean, default=False, index=True)
    is_supplier = Column(Boolean, default=False, index=True)
    partner_category = Column(String(100))  # e.g., "Cloud Computing", "AI/ML"
    partner_description = Column(Text)  # Descrizione servizi
    partner_expertise = Column(JSONB, default=list)  # ["AI", "Cloud", "Security"]
    partner_rating = Column(Float, default=0.0)  # Rating 0-5
    partner_status = Column(String(50), default='active')  # active/inactive
    
    # NEW: Scraping tracking
    last_scraped_at = Column(DateTime)
    scraping_status = Column(String(50), default='pending')  # pending/running/completed/error
    ai_analysis_summary = Column(Text)  # Riassunto AI del contenuto scrappato

    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}', is_partner={self.is_partner})>"

    @property
    def is_categorized(self):
        """True se è partner o supplier"""
        return self.is_partner or self.is_supplier
    
    @property
    def needs_scraping(self):
        """True se ha sito_web ma non è mai stato scrappato o è scaduto"""
        if not self.sito_web:
            return False
        if not self.last_scraped_at:
            return True
        # Re-scrape after 30 days
        from datetime import datetime, timedelta
        return self.last_scraped_at < datetime.now() - timedelta(days=30)
    
    @property
    def has_scraped_content(self):
        """True se ha contenuto scrappato associato"""
        # This will be checked via relationships or separate queries
        return self.scraping_status == 'completed'
