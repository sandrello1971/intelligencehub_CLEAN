from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from passlib.context import CryptContext

from app.core.database import get_db
# from app.routes.auth import get_current_user_dep
from app.schemas.users import (
    UserCreate, UserUpdate, UserResponse, 
    UserListItem, UserDetailResponse
)
from app.models.users import User, Role
from app.models.audit_log import AuditLog

router = APIRouter(prefix="/admin/users", tags=["User Management"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependency temporanea per current_user
async def get_current_user_simple():
    # Mock user per test - sostituire con vera autenticazione
    class MockUser:
        def __init__(self):
            self.id = "96538adf-a127-4cc3-b0a6-13460b39d290"
            self.role = "admin"
            self.email = "s.andrello@enduser-italia.com"
    return MockUser()

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_simple)
):
    """
    Crea un nuovo utente (solo admin)
    """
    # Verifica permessi admin
#     if current_user.role != "admin":
#         raise HTTPException(status_code=403, detail="Accesso negato: serve ruolo admin")
    
    try:
        print(f"🔍 DEBUG: Creating user {user_data.email}")
        # Verifica che email non esista già
        existing = db.query(User).filter(User.email == user_data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email già esistente")
        
        # Hash password
        hashed_password = pwd_context.hash(user_data.password)
        
        # Crea nuovo utente
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=user_data.role,
            permissions=getattr(user_data, "permissions", {}),
            is_active=True
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Log audit
        #         audit_log = AuditLog(
        #             user_id=current_user.id,
        #             action="CREATE_USER",
        #             entity_type="user",
        #             entity_id=str(db_user.id),
        #             new_values={"username": user_data.username, "email": user_data.email, "role": user_data.role}
        #         )
        #         db.add(audit_log)
        #         db.commit()
        
        return UserResponse.model_validate(db_user, from_attributes=True)
        
    except Exception as e:
        print(f"❌ EXCEPTION TYPE: {type(e).__name__}")
        print(f"❌ EXCEPTION MESSAGE: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore creazione utente: {str(e)}")

@router.get("/", response_model=List[UserListItem])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    role: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_simple)
):
    """
    Lista tutti gli utenti (solo admin/manager)
    """
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Accesso negato")
    
    try:
        query = db.query(User)
        
        # Applica filtri
        if role:
            query = query.filter(User.role == role)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        users = query.offset(skip).limit(limit).all()
        
        return [UserListItem.model_validate(u, from_attributes=True) for u in users]
        
    except Exception as e:
        print(f"❌ EXCEPTION TYPE: {type(e).__name__}")
        print(f"❌ EXCEPTION MESSAGE: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Errore recupero utenti: {str(e)}")

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_simple)
):
    """
    Aggiorna un utente esistente
    """
    if current_user.role != "admin" and str(current_user.id) != user_id:
        raise HTTPException(status_code=403, detail="Accesso negato")
    
    try:
        print(f"🔍 DEBUG: Creating user {user_data.email}")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Utente non trovato")
        
        # Salva valori originali per audit
        old_values = {
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active
        }
        
        # Aggiorna campi forniti
        update_data = user_update.dict(exclude_unset=True)
        if "password" in update_data:
            update_data["password_hash"] = pwd_context.hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        # Log audit
        #         audit_log = AuditLog(
        #             user_id=current_user.id,
        #             action="UPDATE_USER",
        #             entity_type="user",
        #             entity_id=str(user.id),
        #             old_values=old_values,
        #             new_values=update_data
        #         )
        #         db.add(audit_log)
        #         db.commit()
        
        return UserResponse.model_validate(user, from_attributes=True)
        
    except Exception as e:
        print(f"❌ EXCEPTION TYPE: {type(e).__name__}")
        print(f"❌ EXCEPTION MESSAGE: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore aggiornamento utente: {str(e)}")

@router.delete("/{user_id}")
async def deactivate_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_simple)
):
    """
    Disattiva un utente (solo admin)
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Accesso negato: serve ruolo admin")
    
    if str(current_user.id) == user_id:
        raise HTTPException(status_code=400, detail="Non puoi disattivare te stesso")
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Utente non trovato")
        
        user.is_active = False
        db.commit()
        
        # Log audit
        #         audit_log = AuditLog(
        #             user_id=current_user.id,
        #             action="DEACTIVATE_USER",
        #             entity_type="user",
        #             entity_id=str(user.id)
        #         )
        #         db.add(audit_log)
        #         db.commit()
        
        return {"message": "Utente disattivato con successo"}
        
    except Exception as e:
        print(f"❌ EXCEPTION TYPE: {type(e).__name__}")
        print(f"❌ EXCEPTION MESSAGE: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore disattivazione utente: {str(e)}")

@router.get("/{user_id}/tickets")
async def get_user_tickets(user_id: str, db: Session = Depends(get_db)):
    """Ottieni tutti i ticket di un utente"""
    from sqlalchemy import text
    
    # Ticket assegnati
    assigned = db.execute(text("""
        SELECT t.*, 'assigned' as relation_type 
        FROM tickets t 
        WHERE t.assigned_to = :user_id
    """), {"user_id": user_id}).fetchall()
    
    # Ticket creati  
    created = db.execute(text("""
        SELECT t.*, 'created' as relation_type 
        FROM tickets t 
        WHERE t.created_by = :user_id
    """), {"user_id": user_id}).fetchall()
    
    return {
        "assigned_tickets": [dict(row) for row in assigned],
        "created_tickets": [dict(row) for row in created]
    }

@router.delete("/{user_id}/permanent")
async def delete_user_permanent(
    user_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_simple)
):
    """
    Cancella definitivamente un utente dal database (solo admin)
    ATTENZIONE: Questa operazione è IRREVERSIBILE
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Accesso negato: serve ruolo admin")
    
    if str(current_user.id) == user_id:
        raise HTTPException(status_code=400, detail="Non puoi cancellare te stesso")
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Utente non trovato")
        
        # Salva info per audit prima della cancellazione
        user_info = f"{user.first_name} {user.last_name} ({user.email})"
        
        # HARD DELETE - rimozione fisica dal database
        db.delete(user)
        db.commit()
        
        return {"message": f"Utente {user_info} cancellato definitivamente dal database"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore cancellazione utente: {str(e)}")
