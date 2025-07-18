# app/main.py - Intelligence Platform FastAPI Application
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.responses import HTMLResponse
import uvicorn

# Import routes
from app.routes import auth
from app.api.v1 import ai_routes
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

# CSP Middleware per risolvere il problema JavaScript eval()
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Content Security Policy che permette unsafe-eval per React
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-eval' 'unsafe-inline' https://cdnjs.cloudflare.com; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' https:; "
        "connect-src 'self' https: wss:; "
        "frame-src 'self';"
    )
    
    # Aggiungi headers di sicurezza
    response.headers["Content-Security-Policy"] = csp
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    return response

# Include routers con prefix che match frontend
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(ai_routes.router, prefix="/api/v1/ai", tags=["ai"])
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
from app.routes import users_complete
app.include_router(users_complete.router, prefix="/api/v1", tags=["users"])
from app.routes import users_complete
app.include_router(users_complete.router, prefix="/api/v1", tags=["users"])

# Route temporanei per utenti
@app.get("/api/v1/users/")
async def list_users_temp():
    from app.database import SessionLocal
    from app.models.users import User
    db = SessionLocal()
    users = db.query(User).all()
    result = []
    for u in users:
        result.append({
            "id": str(u.id),
            "email": u.email,
            "first_name": getattr(u, "first_name", None) or getattr(u, "name", ""),
            "last_name": getattr(u, "last_name", None) or getattr(u, "surname", ""),
            "role": u.role,
            "is_active": u.is_active,
            "crm_id": getattr(u, "crm_id", None)
        })
    db.close()
    return result

@app.get("/api/v1/admin/users/")
async def admin_users_temp():
    from app.database import SessionLocal
    from app.models.users import User
    db = SessionLocal()
    users = db.query(User).all()
    result = []
    for u in users:
        result.append({
            "id": str(u.id),
            "email": u.email,
            "first_name": getattr(u, "first_name", None) or getattr(u, "name", ""),
            "last_name": getattr(u, "last_name", None) or getattr(u, "surname", ""),
            "role": u.role,
            "is_active": u.is_active,
            "crm_id": getattr(u, "crm_id", None)
        })
    db.close()
    return result

@app.delete("/api/v1/admin/users/{user_id}/permanent")
async def delete_user_temp(user_id: str):
    from app.database import SessionLocal
    from app.models.users import User
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
            return {"message": "User deleted successfully"}
        return {"error": "User not found"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()

@app.post("/api/v1/admin/users/")
async def create_user_temp(request: dict):
    from app.database import SessionLocal
    from app.models.users import User
    from passlib.context import CryptContext
    import uuid
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    db = SessionLocal()
    
    try:
        new_user = User(
            id=str(uuid.uuid4()),
            username=request.get("email"),
            email=request.get("email"),
            password_hash=pwd_context.hash(request.get("password", "password123")),
            first_name=request.get("first_name"),
            name=request.get("first_name"),
            last_name=request.get("last_name"),
            surname=request.get("last_name"),
            role=request.get("role", "operator"),
            is_active=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"id": str(new_user.id), "message": "User created successfully"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()

@app.patch("/api/v1/admin/users/{user_id}")
async def update_user_temp(user_id: str, request: dict):
    from app.database import SessionLocal
    from app.models.users import User
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}
        
        # Aggiorna i campi forniti
        if "first_name" in request:
            user.first_name = request["first_name"]
            user.name = request["first_name"]  # Compatibilità
        if "last_name" in request:
            user.last_name = request["last_name"]
            user.surname = request["last_name"]  # Compatibilità
        if "email" in request:
            user.email = request["email"]
            user.username = request["email"]  # Username = email
        if "role" in request:
            user.role = request["role"]
        if "crm_id" in request and request["crm_id"]:
            user.crm_id = int(request["crm_id"])
        
        db.commit()
        return {"message": "User updated successfully"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()
from app.routes import tasks_global
app.include_router(tasks_global.router)
