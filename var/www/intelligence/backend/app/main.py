# app/main.py - Intelligence Platform FastAPI Application
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

# Import routes
from app.routes import auth
from app.api.v1 import ai_routes
from app.routes import admin_users
from app.routes import companies  # 🆕 Added companies import
from app.routes import kit_commerciali
from app.routes import tipologie_servizi
from app.routes import partner
from app.routes import articles
from app.services.web_scraping import api_routes_working

# Database
from app.database import create_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Intelligence Platform API...")
    create_tables()
    print("✅ Database tables initialized")
    yield
    # Shutdown
    print("🛑 Shutting down Intelligence Platform API...")

# FastAPI app
app = FastAPI(
    title="Intelligence Platform API",
    description="AI-Powered Business Intelligence Platform",
    version="5.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers con prefix che match frontend
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(ai_routes.router, prefix="/api/v1/ai", tags=["ai"])
app.include_router(admin_users.router, prefix="/api/v1", tags=["users"])
app.include_router(companies.router, tags=["companies"])  # 🆕 Added companies router
app.include_router(articles.router, prefix="/api/v1", tags=["articles"])
app.include_router(kit_commerciali.router, prefix="/api/v1", tags=["kit"])
app.include_router(tipologie_servizi.router, prefix="/api/v1", tags=["tipologie"])
app.include_router(partner.router, prefix="/api/v1", tags=["partner"])
app.include_router(api_routes_working.router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Intelligence Platform API v5.0",
        "status": "healthy",
        "docs": "/docs",
        "endpoints": {
            "auth": "/api/v1/auth/login",
            "user_profile": "/api/v1/auth/me",
            "ai_chat": "/api/v1/ai/chat",
            "companies": "/api/v1/companies/",
            "articles": "/api/v1/articles/",
        }
    }

# Health check
@app.get("/health")
async def health():
    return {"status": "healthy", "version": "5.0"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
