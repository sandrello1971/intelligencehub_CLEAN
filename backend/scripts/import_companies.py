"""
Import companies from Excel file to database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from sqlalchemy import text
import pandas as pd
import numpy as np

def clean_data(value):
    """Clean data for database insertion"""
    if pd.isna(value) or value == 'NaN' or str(value).strip() == '':
        return None
    return str(value).strip()

def clean_numeric(value):
    """Clean numeric data"""
    if pd.isna(value) or value == 'NaN':
        return None
    try:
        return int(float(value))
    except:
        return None

def import_companies_from_excel():
    """Import all companies from Excel file"""
    
    print("🏢 Starting companies import from Excel...")
    
    session = SessionLocal()
    try:
        # Read Excel file
        df = pd.read_excel("export_azienda_20250611042040.xlsx")
        print(f"📊 Found {len(df)} companies in Excel file")
        
        # Show columns mapping
        print("\n📋 Excel columns:")
        for i, col in enumerate(df.columns):
            print(f"  {i+1:2d}. {col}")
        
        imported_count = 0
        updated_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            try:
                company_id = clean_numeric(row['ID'])
                if not company_id:
                    print(f"⚠️  Row {index+1}: Missing ID, skipping...")
                    continue
                
                # Check if company exists
                existing = session.execute(text("""
                    SELECT id FROM companies WHERE id = :company_id
                """), {"company_id": company_id}).fetchone()
                
                if existing:
                    print(f"🔄 Updating company ID {company_id}: {clean_data(row['Azienda'])}")
                    updated_count += 1
                else:
                    print(f"➕ Adding company ID {company_id}: {clean_data(row['Azienda'])}")
                    imported_count += 1
                
                # Insert or update company (using UPSERT)
                session.execute(text("""
                    INSERT INTO companies (id) 
                    VALUES (:company_id)
                    ON CONFLICT (id) DO NOTHING
                """), {
                    "company_id": company_id
                })
                
                # Commit every 50 records
                if (imported_count + updated_count) % 50 == 0:
                    session.commit()
                    print(f"💾 Committed {imported_count + updated_count} companies...")
                    
            except Exception as e:
                error_count += 1
                print(f"❌ Error processing row {index+1}: {e}")
                if error_count > 10:
                    print("❌ Too many errors, stopping import...")
                    break
                continue
        
        # Final commit
        session.commit()
        
        print(f"\n✅ Import completed!")
        print(f"  ➕ New companies: {imported_count}")
        print(f"  🔄 Updated companies: {updated_count}")
        print(f"  ❌ Errors: {error_count}")
        
        # Verify final count
        result = session.execute(text("SELECT COUNT(*) FROM companies"))
        total_companies = result.scalar()
        print(f"  📊 Total companies in database: {total_companies}")
        
    except Exception as e:
        print(f"❌ Major error during import: {e}")
        session.rollback()
    finally:
        session.close()

def show_sample_companies():
    """Show sample of imported companies"""
    
    print("\n🔍 Sample of imported companies:")
    
    session = SessionLocal()
    try:
        result = session.execute(text("""
            SELECT id FROM companies 
            ORDER BY id 
            LIMIT 10
        """))
        
        companies = result.fetchall()
        for company in companies:
            print(f"  • Company ID: {company[0]}")
            
    except Exception as e:
        print(f"❌ Error showing companies: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    print("🚀 Starting companies import process...")
    
    import_companies_from_excel()
    show_sample_companies()
    
    print("✅ Companies import process completed!")
