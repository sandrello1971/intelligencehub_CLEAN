# app/database.py - Database Configuration
import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Fallback configuration
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_NAME = os.getenv("DB_NAME", "intelligence")
    DB_USER = os.getenv("DB_USER", "intelligence_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "intelligence_pass")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False  # Set to True for SQL debugging
)

# Create SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to create tables (required by main.py)
def create_tables():
    """
    Create all database tables.
    Note: In production, use Alembic migrations instead.
    """
    try:
        # Import all models to ensure they're registered with Base
        from app.models import (
            users, company, contact, activity, task, ticket,
            ai_conversation, audit_log, hashtag, other
        )
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        # Don't fail startup if tables already exist
        pass

# Test database connection
def test_connection():
    """Test database connection"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).fetchone()
            return True
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

# Initialize database on import
if __name__ == "__main__":
    print("🔧 Testing database connection...")
    if test_connection():
        print("✅ Database connection successful")
        create_tables()
    else:
        print("❌ Database connection failed")
