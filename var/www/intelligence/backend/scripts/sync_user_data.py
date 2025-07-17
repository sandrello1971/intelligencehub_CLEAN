"""
Sync users and authentication data properly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from sqlalchemy import text

def sync_user_auth_data():
    """Sync users table with local_users authentication data"""
    
    print("🔄 Syncing user authentication data...")
    
    session = SessionLocal()
    try:
        # Get all users with their auth data
        result = session.execute(text("""
            SELECT 
                u.id,
                u.name,
                u.surname, 
                u.email,
                lu.password,
                lu.role,
                lu.must_change_password
            FROM users u
            LEFT JOIN local_users lu ON u.email = lu.email
            ORDER BY u.id
        """))
        
        users_data = result.fetchall()
        print(f"📋 Processing {len(users_data)} users...")
        
        synced_count = 0
        missing_auth = 0
        
        for user in users_data:
            user_id, name, surname, email, password, role, must_change = user
            
            if password and role:
                print(f"✅ {name} {surname} ({email}) - Role: {role}")
                synced_count += 1
            else:
                print(f"⚠️  {name} {surname} ({email}) - MISSING AUTH DATA")
                missing_auth += 1
        
        print(f"\n📊 Summary:")
        print(f"✅ Users with auth data: {synced_count}")
        print(f"⚠️  Users missing auth data: {missing_auth}")
        
        # Find the admin user specifically
        stefano = session.execute(text("""
            SELECT u.id, u.name, u.surname, u.email, lu.role
            FROM users u
            LEFT JOIN local_users lu ON u.email = lu.email
            WHERE u.email LIKE '%s.andrello%' OR u.email LIKE '%stefano%'
        """)).fetchall()
        
        if stefano:
            print(f"\n👤 Found Stefano:")
            for user in stefano:
                print(f"  • ID {user[0]}: {user[1]} {user[2]} ({user[3]}) - Role: {user[4]}")
        else:
            print(f"\n❌ Stefano not found in users")
            
    except Exception as e:
        print(f"❌ Error syncing user data: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    sync_user_auth_data()
