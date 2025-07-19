from fastapi import APIRouter, HTTPException
import os

router = APIRouter(prefix="/auth/google", tags=["Google Auth"])

@router.get("/login")
async def google_login():
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
    
    auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope=openid email profile https://www.googleapis.com/auth/spreadsheets.readonly&"
        f"response_type=code&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    
    return {"authorization_url": auth_url}

@router.get("/callback")
async def google_callback(code: str = None):
    """Callback semplificato per debug"""
    if not code:
        raise HTTPException(status_code=400, detail="Codice mancante")
    
    return {"success": True, "message": "Login Google riuscito!", "code_received": code[:10] + "..."}

@router.get("/test")
async def test_google_config():
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    return {
        "client_id": client_id[:20] + "..." if client_id else "NOT_SET",
        "status": "simple_version"
    }
