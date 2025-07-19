from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError

from app.core.database import get_db
from app.schemas.auth_schemas import LoginRequest, LoginResponse, UserProfile
from app.core.config import settings

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
# Importa configurazioni da settings
from app.core.config import settings
SECRET_KEY = settings.JWT_SECRET
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """User login endpoint"""
    
    # Query user from database
    result = db.execute(text("""
        SELECT 
            u.id, u.name, u.surname, u.email,
            u.password_hash as password, u.role, u.must_change_password
        FROM users u
        WHERE u.email = :email
    """), {"email": login_data.username})
    
    user_data = result.fetchone()
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(login_data.password, user_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user_data.id)}, expires_delta=access_token_expires
    )
    
    # Update last login
    db.execute(text("""
        UPDATE users SET last_login = :last_login WHERE id = :user_id
    """), {"last_login": datetime.now(), "user_id": user_data.id})
    db.commit()
    
    # Return login response
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        must_change_password=bool(user_data.must_change_password),
        user={
            "id": str(user_data.id),
            "username": user_data.email,
            "name": user_data.name,
            "surname": user_data.surname,
            "first_name": user_data.name,
            "last_name": user_data.surname,
            "email": user_data.email,
            "role": user_data.role,
            "permissions": {},
            "is_active": True,
            "last_login": datetime.now(),
            "must_change_password": user_data.must_change_password,
        }
    )

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.get("/me")
async def get_current_user_profile():
    """Get current user profile - simple version"""
    return {
        "id": "96538adf-a127-4cc3-b0a6-13460b39d290",
        "username": "s.andrello@enduser-italia.com", 
        "email": "s.andrello@enduser-italia.com",
        "first_name": "Stefano",
        "last_name": "Andrello",
        "role": "admin",
        "is_active": True,
        "created_at": "2025-07-04T12:28:45.354647"
    }

def get_current_user_dep():
    """Dependency to get current user from JWT token"""
    # For now, return a dummy function
    # In production, this would decode JWT and return user
    def _get_current_user():
        return {"id": "dummy-user", "email": "dummy@example.com", "role": "admin"}
    return _get_current_user


from pydantic import BaseModel

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str = None

@router.post("/change-password")
async def change_password_api(
    request: ChangePasswordRequest,
    db: Session = Depends(get_db)
):
    """Change user password"""
    try:
        user_email = "s.andrello@enduser-italia.com"  # Hardcoded per ora
        
        # Verifica utente attuale
        result = db.execute(text("""
            SELECT id, password_hash FROM users WHERE email = :email
        """), {"email": user_email})
        
        user_data = result.fetchone()
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Verifica password attuale
        if not pwd_context.verify(request.current_password, user_data.password_hash):
            raise HTTPException(status_code=401, detail="Current password is incorrect")
        
        # Hash nuova password
        new_password_hash = pwd_context.hash(request.new_password)
        
        # Aggiorna password e rimuovi flag must_change_password
        db.execute(text("""
            UPDATE users 
            SET password_hash = :new_password_hash, 
                must_change_password = false
            WHERE id = :user_id
        """), {
            "new_password_hash": new_password_hash,
            "user_id": user_data.id
        })
        
        db.commit()
        
        return {"message": "Password changed successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# JWT utilities
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends

security = HTTPBearer()

async def get_current_user_from_jwt(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Decode JWT token and get current user"""
    try:
        # Decode JWT token
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user from database (supporta sia ID che email)
        if '@' in user_id:
            # Se contiene @, è un'email
            result = db.execute(text("""
                SELECT id, email, first_name, last_name, role, is_active 
                FROM users WHERE email = :user_id
            """), {"user_id": user_id})
        else:
            # Altrimenti è un ID
            result = db.execute(text("""
                SELECT id, email, first_name, last_name, role, is_active 
                FROM users WHERE id = :user_id
            """), {"user_id": user_id})
        
        user_data = result.fetchone()
        if not user_data:
            raise HTTPException(status_code=401, detail="User not found")
        
        if not user_data.is_active:
            raise HTTPException(status_code=401, detail="User inactive")
            
        return user_data
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/change-password")
async def change_password_jwt(
    request: ChangePasswordRequest,
    current_user = Depends(get_current_user_from_jwt),
    db: Session = Depends(get_db)
):
    """Change user password with JWT authentication"""
    try:
        # Verifica password attuale
        result = db.execute(text("""
            SELECT password_hash FROM users WHERE id = :user_id
        """), {"user_id": current_user.id})
        
        user_data = result.fetchone()
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Verifica password attuale
        if not pwd_context.verify(request.current_password, user_data.password_hash):
            raise HTTPException(status_code=401, detail="Current password is incorrect")
        
        # Hash nuova password
        new_password_hash = pwd_context.hash(request.new_password)
        
        # Aggiorna password e rimuovi flag must_change_password
        db.execute(text("""
            UPDATE users 
            SET password_hash = :new_password_hash, 
                must_change_password = false
            WHERE id = :user_id
        """), {
            "new_password_hash": new_password_hash,
            "user_id": current_user.id
        })
        
        db.commit()
        
        return {
            "message": "Password changed successfully",
            "user": f"{current_user.first_name} {current_user.last_name}"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# JWT utilities
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends

security = HTTPBearer()

async def get_current_user_from_jwt(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Decode JWT token and get current user"""
    try:
        # Decode JWT token
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user from database (supporta sia ID che email)
        if '@' in user_id:
            # Se contiene @, è un'email
            result = db.execute(text("""
                SELECT id, email, first_name, last_name, role, is_active 
                FROM users WHERE email = :user_id
            """), {"user_id": user_id})
        else:
            # Altrimenti è un ID
            result = db.execute(text("""
                SELECT id, email, first_name, last_name, role, is_active 
                FROM users WHERE id = :user_id
            """), {"user_id": user_id})
        
        user_data = result.fetchone()
        if not user_data:
            raise HTTPException(status_code=401, detail="User not found")
        
        if not user_data.is_active:
            raise HTTPException(status_code=401, detail="User inactive")
            
        return user_data
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/change-password")
async def change_password_jwt(
    request: ChangePasswordRequest,
    current_user = Depends(get_current_user_from_jwt),
    db: Session = Depends(get_db)
):
    """Change user password with JWT authentication"""
    try:
        # Verifica password attuale
        result = db.execute(text("""
            SELECT password_hash FROM users WHERE id = :user_id
        """), {"user_id": current_user.id})
        
        user_data = result.fetchone()
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Verifica password attuale
        if not pwd_context.verify(request.current_password, user_data.password_hash):
            raise HTTPException(status_code=401, detail="Current password is incorrect")
        
        # Hash nuova password
        new_password_hash = pwd_context.hash(request.new_password)
        
        # Aggiorna password e rimuovi flag must_change_password
        db.execute(text("""
            UPDATE users 
            SET password_hash = :new_password_hash, 
                must_change_password = false
            WHERE id = :user_id
        """), {
            "new_password_hash": new_password_hash,
            "user_id": current_user.id
        })
        
        db.commit()
        
        return {
            "message": "Password changed successfully",
            "user": f"{current_user.first_name} {current_user.last_name}"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Alias for backward compatibility
get_current_user = get_current_user_profile

@router.get("/profile")
async def get_user_profile(
    current_user = Depends(get_current_user_from_jwt),
    db: Session = Depends(get_db)
):
    """Get current user profile"""
    try:
        # Ottieni dati completi utente
        result = db.execute(text("""
            SELECT id, username, email, first_name, last_name, name, surname, 
                   role, is_active, last_login, must_change_password
            FROM users WHERE id = :user_id
        """), {"user_id": current_user.id})
        
        user_data = result.fetchone()
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "id": str(user_data.id),
            "username": user_data.username,
            "email": user_data.email,
            "first_name": user_data.first_name or user_data.name,
            "last_name": user_data.last_name or user_data.surname,
            "role": user_data.role,
            "is_active": user_data.is_active,
            "last_login": user_data.last_login.isoformat() if user_data.last_login else None,
            "must_change_password": user_data.must_change_password or False,
            "permissions": {}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
