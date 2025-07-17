"""
Migration script to import existing users and companies data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine
from sqlalchemy import text
import pandas as pd

def migrate_users():
    """Migrate users from existing tables to new schema"""
    
    print("👤 Migrating users...")
    
    session = SessionLocal()
    try:
        # Get users data with authentication info
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
        print(f"📋 Found {len(users_data)} users to migrate")
        
        # Check if our users table has the right structure
        result = session.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND table_schema = 'public'
            ORDER BY ordinal_position
        """))
        
        columns = result.fetchall()
        print("📋 Current users table structure:")
        for col in columns:
            print(f"  • {col[0]}: {col[1]}")
            
        return users_data
        
    except Exception as e:
        print(f"❌ Error migrating users: {e}")
        session.rollback()
        return []
    finally:
        session.close()

def migrate_companies_from_excel():
    """Import companies from Excel file"""
    
    print("🏢 Importing companies from Excel...")
    
    try:
        # Read the Excel file
        excel_file = "export_azienda_20250611042040.xlsx"
        if os.path.exists(excel_file):
            df = pd.read_excel(excel_file)
            print(f"📊 Found Excel file with {len(df)} companies")
            print(f"📋 Columns: {list(df.columns)}")
            
            # Show first few rows
            print("\n📋 First 3 companies:")
            print(df.head(3).to_string())
            
            return df
        else:
            print(f"❌ Excel file {excel_file} not found")
            return None
            
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Starting data migration...")
    
    # Migrate users
    users = migrate_users()
    
    # Import companies
    companies_df = migrate_companies_from_excel()
    
    print("✅ Migration analysis completed!")
