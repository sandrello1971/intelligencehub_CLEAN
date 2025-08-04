from dotenv import load_dotenv
load_dotenv()

# app/main.py - Intelligence Platform FastAPI Application
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.responses import HTMLResponse
import uvicorn
import time
from collections import defaultdict, deque
from typing import Dict, Deque
from datetime import datetime, timedelta
# Import routes
from app.routes import auth
from app.api.v1 import ai_routes
from app.routes import companies  # 🆕 Added companies import
from app.routes import kit_commerciali
from app.routes import tipologie_servizi
from app.routes import partner
from app.routes import articles
from app.services.web_scraping import api_routes_working
from app.routes import wiki
from app.routes import rag_routes
from app.routes import intellivoice_record

# Database
from app.database import create_tables
# Rate limiting storage (in-memory, non invasivo)
request_counts: Dict[str, Deque[float]] = defaultdict(lambda: deque(maxlen=100))
blocked_ips: Dict[str, float] = {}  # IP -> timestamp when block expires


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


# Security middleware da aggiungere DOPO il middleware CORS esistente
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()
    
    # 1. Verifica se IP è temporaneamente bloccato
    if client_ip in blocked_ips:
        if current_time < blocked_ips[client_ip]:
            # IP ancora bloccato
            return Response(
                content="Rate limit exceeded. Access temporarily restricted.",
                status_code=429,
                headers={"Retry-After": "300"}  # 5 minuti
            )
        else:
            # Rimuovi blocco scaduto
            del blocked_ips[client_ip]
    
    # 2. Rate limiting: max 60 richieste per minuto per IP
    minute_ago = current_time - 60
    ip_requests = request_counts[client_ip]
    
    # Rimuovi richieste vecchie
    while ip_requests and ip_requests[0] < minute_ago:
        ip_requests.popleft()
    
    # Controlla limite
    if len(ip_requests) >= 60:  # 60 req/min
        # Blocca IP per 5 minuti
        blocked_ips[client_ip] = current_time + 300
        print(f"🚨 SECURITY: IP {client_ip} blocked for rate limiting")
        return Response(
            content="Too many requests. Access temporarily restricted.",
            status_code=429,
            headers={"Retry-After": "300"}
        )
    
    # 3. Blocca metodi HTTP sospetti
    suspicious_methods = ["OPTIONS", "TRACE", "CONNECT"]
    if request.method in suspicious_methods:
        print(f"🚨 SECURITY: Blocked {request.method} from {client_ip}")
        return Response(
            content="Method not allowed",
            status_code=405,
            headers={"Allow": "GET, POST, PUT, DELETE"}
        )
    
    # 4. Blocca pattern URL sospetti
    suspicious_patterns = [
        "/nice%20ports", "/Trinity.txt", "/devicedesc.xml",
        "/webui", "/owa/", "/.env", "/config", "/admin/phpmyadmin", "/admin/login", "/admin/panel"
    ]
    
    url_path = str(request.url.path).lower()
    for pattern in suspicious_patterns:
        if pattern.lower() in url_path:
            print(f"🚨 SECURITY: Blocked suspicious URL {url_path} from {client_ip}")
            return Response(content="Not Found", status_code=404)
    
    # 5. Log richiesta normale
    ip_requests.append(current_time)
    
    # Processa richiesta normale
    response = await call_next(request)
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
from app.routes import tasks
from app.routes.auth_google import router as google_auth_router
app.include_router(tasks_global.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(google_auth_router)

# Workflow Configuration Routes
from app.routes.admin import workflow_config, workflow_management

app.include_router(workflow_config.router)
app.include_router(workflow_management.router)


from app.routes.admin import milestone_templates
app.include_router(milestone_templates.router)
app.include_router(wiki.router, prefix="/api/v1", tags=["wiki"])
app.include_router(rag_routes.router, prefix="/api/v1", tags=["rag"])

from app.routes import templates
from app.routes import servizi_template
from app.routes import tickets
app.include_router(templates.router)
app.include_router(servizi_template.router)
app.include_router(tickets.router, prefix="/api/v1", tags=["tickets"])
