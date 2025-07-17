"""
Database migration script per Web Scraping V2
Crea le nuove tabelle senza toccare quelle esistenti
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from .models import Base
import logging

logger = logging.getLogger(__name__)

def migrate_database():
    """Crea le nuove tabelle V2"""
    try:
        # Database connection
        database_url = os.getenv("DATABASE_URL", "postgresql://intelligence_user:intelligence_pass@localhost:5432/intelligence")
        engine = create_engine(database_url)
        
        # Create only V2 tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Database migration completed successfully")
        logger.info("New tables created:")
        logger.info("- scraped_documents_v2")
        logger.info("- document_chunks_v2")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database migration failed: {e}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    migrate_database()
