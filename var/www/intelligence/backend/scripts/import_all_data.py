"""
Complete data import script for Intelligence AI Platform
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine
from sqlalchemy import text
import pandas as pd
from datetime import datetime

def analyze_and_import_companies():
    """Import companies from Excel into companies table"""
    
    print("🏢 Importing companies from Excel...")
    
    session = SessionLocal()
    try:
        # Read Excel file
        df = pd.read_excel("export_azienda_20250611042040.xlsx")
        print(f"📊 Found {len(df)} companies in Excel")
        
        # Clean and prepare data
        imported_count = 0
        for index, row in df.iterrows():
            try:
                # Check if company already exists
                existing = session.execute(text("""
                    SELECT id FROM companies WHERE id = :company_id
                """), {"company_id": int(row['ID'])}).fetchone()
                
                if existing:
                    print(f"⚠️  Company ID {row['ID']} already exists, skipping...")
                    continue
                
                # Insert company data
                session.execute(text("""
                    INSERT INTO companies (id) VALUES (:company_id)
                """), {
                    "company_id": int(row['ID'])
                })
                
                imported_count += 1
                
                if imported_count % 50 == 0:
                    print(f"📊 Imported {imported_count} companies...")
                    
            except Exception as e:
                print(f"❌ Error importing company {row['ID']}: {e}")
                continue
        
        session.commit()
        print(f"✅ Successfully imported {imported_count} companies!")
        
    except Exception as e:
        print(f"❌ Error importing companies: {e}")
        session.rollback()
    finally:
        session.close()

def test_existing_data():
    """Test and display existing data structure"""
    
    print("🔍 Testing existing data...")
    
    session = SessionLocal()
    try:
        # Count existing records
        users_count = session.execute(text("SELECT COUNT(*) FROM users")).scalar()
        companies_count = session.execute(text("SELECT COUNT(*) FROM companies")).scalar()
        tasks_count = session.execute(text("SELECT COUNT(*) FROM tasks")).scalar()
        
        print(f"📊 Current data counts:")
        print(f"  👤 Users: {users_count}")
        print(f"  🏢 Companies: {companies_count}")
        print(f"  📋 Tasks: {tasks_count}")
        
        # Show sample user data
        print("\n👤 Sample users:")
        users = session.execute(text("""
            SELECT u.id, u.name, u.surname, u.email, lu.role 
            FROM users u 
            LEFT JOIN local_users lu ON u.email = lu.email 
            LIMIT 5
        """)).fetchall()
        
        for user in users:
            print(f"  • {user[0]}: {user[1]} {user[2]} ({user[3]}) - {user[4]}")
            
    except Exception as e:
        print(f"❌ Error testing data: {e}")
    finally:
        session.close()

def create_admin_user():
    """Create/update admin user for testing"""
    
    print("👤 Setting up admin user...")
    
    session = SessionLocal()
    try:
        # Check if s.andrello@enduser-italia.com exists
        admin_email = "s.andrello@enduser-italia.com"
        
        admin_user = session.execute(text("""
            SELECT u.id, u.name, u.surname, u.email 
            FROM users u 
            WHERE u.email = :email
        """), {"email": admin_email}).fetchone()
        
        if admin_user:
            print(f"✅ Admin user found: {admin_user[1]} {admin_user[2]} (ID: {admin_user[0]})")
            
            # Check auth data
            auth_data = session.execute(text("""
                SELECT role, must_change_password 
                FROM local_users 
                WHERE email = :email
            """), {"email": admin_email}).fetchone()
            
            if auth_data:
                print(f"🔑 Auth data: Role={auth_data[0]}, Must change password={auth_data[1]}")
            else:
                print("⚠️  No auth data found for admin user")
        else:
            print("❌ Admin user not found")
            
    except Exception as e:
        print(f"❌ Error checking admin user: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    print("🚀 Starting complete data import process...")
    
    # Test existing data
    test_existing_data()
    
    # Import companies
    analyze_and_import_companies()
    
    # Setup admin user
    create_admin_user()
    
    print("✅ Data import process completed!")
