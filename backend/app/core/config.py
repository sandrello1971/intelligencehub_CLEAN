# app/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional, List
import json

class Settings(BaseSettings):
    # Base settings
    PROJECT_NAME: str = "IntelligenceHUB"
    VERSION: str = "5.0.0"
    DEBUG: bool = False
    
    # Domain and URLs
    DOMAIN: str = "intelligencehub.enduser-digital.com"
    API_BASE_URL: str = "https://intelligencehub.enduser-digital.com/api"
    FRONTEND_URL: str = "https://intelligencehub.enduser-digital.com"
    
    # Database settings
    DATABASE_URL: str = "postgresql://intelligence_user:intelligence_pass@localhost:5432/intelligence"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "intelligence_user"
    DB_PASSWORD: str = "intelligence_pass"
    DB_NAME: str = "intelligence"
    
    # Security/JWT
    SECRET_KEY: str = "EU1nt3ll1g3nc3_2025!"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # CRM Settings
    CRM_USERNAME: str = "intellivoice@enduser-digital.com"
    CRM_PASSWORD: str = "B4b4in4_07"
    CRM_API_KEY: str = "r5l50i5lvd.YjuIXg0PPJnqzeldzCBlEpMlwqJPRPFgJppSkPu"
    CRM_BASE_URL: str = "https://api.crmincloud.it"
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_KEY_HERE") 
    OPENAI_MODEL: str = "gpt-4-turbo"
    
    # Email/SMTP
    SMTP_SERVER: str = "ssl0.ovh.net"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = "intellivoice@enduser-digital.com"
    SMTP_PASSWORD: str = "EuIntellivoice!2025"
    EMAIL_FROM: str = "intellivoice@enduser-digital.com"
    EMAIL_FROM_NAME: str = "Intelligence Hub"
    ENABLE_EMAIL_NOTIFICATIONS: bool = True
    
    # SLA Settings
    SLA_WARNING_DAYS: int = 2
    SLA_CHECK_HOURS: str = "09:00,14:00,17:00"
    
    # Qdrant Vector DB
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_TIMEOUT: int = 30
    QDRANT_COLLECTION_NAME: str = "intelligence_knowledge"
    
    # RAG Settings
    RAG_CHUNK_SIZE: int = 1000
    RAG_CHUNK_OVERLAP: int = 200
    RAG_SIMILARITY_THRESHOLD: float = 0.7
    RAG_MAX_RESULTS: int = 10
    
    # FastAPI Settings
    FASTAPI_HOST: str = "0.0.0.0"
    FASTAPI_PORT: int = 8000
    FASTAPI_DEBUG: bool = True
    FASTAPI_RELOAD: bool = True
    
    # CORS Settings
    CORS_ORIGINS: str = '["https://intelligencehub.enduser-digital.com", "http://localhost:3000"]'
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: str = '["*"]'
    CORS_HEADERS: str = '["*"]'
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # Ignore extra fields to prevent validation errors
        extra = "ignore"

settings = Settings()
