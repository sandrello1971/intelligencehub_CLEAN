#!/usr/bin/env python3
import sys
import os
sys.path.append('/var/www/intelligence/backend')

from passlib.context import CryptContext
import psycopg2
from datetime import datetime

# Password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database connection
conn = psycopg2.connect(
    host="localhost",
    database="intelligence",
    user="intelligence_user",
    password="intelligence_pass"
)

def create_admin_user():
    """Crea utente admin Stefano Andrello"""
    
    # Hash password
    password_hash = pwd_context.hash("password123")
    
    # SQL Insert
    sql = """
    INSERT INTO users (
        username, email, password_hash, role, name, surname, 
        first_name, last_name, permissions, is_active, created_at
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
    """
    
    values = (
        "s.andrello@enduser-italia.com",  # username (email)
        "s.andrello@enduser-italia.com",  # email
        password_hash,                     # password_hash
        "admin",                          # role
        "Stefano Andrello",               # name
        "Andrello",                       # surname
        "Stefano",                        # first_name
        "Andrello",                       # last_name
        '{"admin": true, "manage_users": true, "view_all": true}',  # permissions
        True,                             # is_active
        datetime.now()                    # created_at
    )
    
    try:
        cursor = conn.cursor()
        cursor.execute(sql, values)
        conn.commit()
        print("✅ Utente Stefano Andrello creato con successo!")
        print("📧 Email: s.andrello@enduser-italia.com")
        print("🔐 Password: password123 (da cambiare al primo accesso)")
        print("👨‍💼 Ruolo: admin")
        cursor.close()
        
    except Exception as e:
        print(f"❌ Errore creazione utente: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_admin_user()
