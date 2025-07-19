from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
import os
import json
import requests
from datetime import datetime

from app.core.database import get_db
from app.auth.jwt_handler import create_access_token

router = APIRouter(prefix="/auth/google", tags=["Google Auth"])

@router.get("/login")
async def google_login():
    """Inizia login Google"""
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
    
    auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope=openid%20email%20profile%20https://www.googleapis.com/auth/spreadsheets.readonly&"
        f"response_type=code&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    
    return {"authorization_url": auth_url}

@router.get("/callback")
async def google_callback(code: str = None, db: Session = Depends(get_db)):
    """Callback Google OAuth - Salva utente e crea sessione"""
    if not code:
        raise HTTPException(status_code=400, detail="Codice autorizzazione mancante")
    
    try:
        # Exchange code per token
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
        
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri
        }
        
        response = requests.post(token_url, data=token_data)
        tokens = response.json()
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Errore token: {tokens}")
        
        # Ottieni info utente da Google
        user_info_url = f"https://www.googleapis.com/oauth2/v1/userinfo?access_token={tokens['access_token']}"
        user_response = requests.get(user_info_url)
        user_info = user_response.json()
        
        if user_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Errore recupero dati utente")
        
        # Cerca utente esistente o crea nuovo
        existing_user = db.execute(text("""
            SELECT id, email, role FROM users WHERE email = :email
        """), {"email": user_info['email']}).fetchone()
        
        if existing_user:
            # Aggiorna utente esistente con credenziali Google
            user_id = existing_user[0]
            
            # Salva Google credentials
            google_creds = json.dumps({
                'token': tokens['access_token'],
                'refresh_token': tokens.get('refresh_token'),
                'token_uri': "https://oauth2.googleapis.com/token",
                'client_id': client_id,
                'client_secret': client_secret,
                'scopes': ['openid', 'email', 'profile', 'https://www.googleapis.com/auth/spreadsheets.readonly'],
                'expiry': None
            })
            
            db.execute(text("""
                UPDATE users SET 
                    google_id = :google_id,
                    google_credentials = :google_credentials,
                    auto_sync_enabled = TRUE,
                    last_login = :last_login,
                    last_sync_at = :last_sync_at
                WHERE email = :email
            """), {
                "google_id": user_info['id'],
                "google_credentials": google_creds,
                "last_login": datetime.utcnow(),
                "last_sync_at": datetime.utcnow(),
                "email": user_info['email']
            })
            
            username = existing_user[1]  # email come username
            
        else:
            # Crea nuovo utente (solo se email autorizzata)
            authorized_emails = [
                "s.andrello@enduser-italia.com",
                "p.menin@enduser-italia.com",
                "g.fulgheri@enduser-italia.com",
                "f.corbinelli@enduser-italia.com",
                "f.devita@enduser-italia.com",
                "f.aliboni@enduser-italia.com",
                "ms.gentile@enduser-italia.com"
            ]
            
            if user_info['email'] not in authorized_emails:
                raise HTTPException(status_code=403, detail="Email non autorizzata per accedere al sistema")
            
            # Determina ruolo basato su email
            role = "operator"
            if user_info['email'] == "s.andrello@enduser-italia.com":
                role = "admin"
            elif user_info['email'] in ["f.aliboni@enduser-italia.com", "ms.gentile@enduser-italia.com"]:
                role = "area_manager"
            elif user_info['email'] in ["p.menin@enduser-italia.com", "g.fulgheri@enduser-italia.com", "f.corbinelli@enduser-italia.com", "f.devita@enduser-italia.com"]:
                role = "account_manager"
            
            google_creds = json.dumps({
                'token': tokens['access_token'],
                'refresh_token': tokens.get('refresh_token'),
                'token_uri': "https://oauth2.googleapis.com/token",
                'client_id': client_id,
                'client_secret': client_secret,
                'scopes': ['openid', 'email', 'profile', 'https://www.googleapis.com/auth/spreadsheets.readonly']
            })
            
            # Genera UUID per nuovo utente
            import uuid
            user_id = str(uuid.uuid4())
            
            db.execute(text("""
                INSERT INTO users (
                    id, username, email, first_name, last_name, name, surname,
                    role, is_active, google_id, google_credentials, 
                    auto_sync_enabled, last_login, last_sync_at
                ) VALUES (
                    :id, :username, :email, :first_name, :last_name, :name, :surname,
                    :role, TRUE, :google_id, :google_credentials,
                    TRUE, :last_login, :last_sync_at
                )
            """), {
                "id": user_id,
                "username": user_info['email'],
                "email": user_info['email'],
                "first_name": user_info.get('given_name', ''),
                "last_name": user_info.get('family_name', ''),
                "name": user_info.get('given_name', ''),
                "surname": user_info.get('family_name', ''),
                "role": role,
                "google_id": user_info['id'],
                "google_credentials": google_creds,
                "last_login": datetime.utcnow(),
                "last_sync_at": datetime.utcnow()
            })
            
            username = user_info['email']
        
        db.commit()
        
        # Crea JWT token per il sistema
        access_token = create_access_token(data={"sub": username})
        
        # Redirect al frontend con token
        frontend_url = os.getenv("FRONTEND_URL")
        return RedirectResponse(
            url=f"{frontend_url}/auth/success?token={access_token}&user={user_info['given_name']}"
        )
        
    except Exception as e:
        print(f"\n=== DEBUG ERROR ==\n{str(e)}\n{type(e)}\n================")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore login: {str(e)}")

@router.get("/test")
async def test_google_config():
    """Test configurazione Google"""
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    if not client_id:
        return {"error": "GOOGLE_CLIENT_ID non configurato"}
    
    return {
        "client_id": client_id[:20] + "...",
        "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI"),
        "frontend_url": os.getenv("FRONTEND_URL"),
        "status": "configured"
    }
