#!/usr/bin/env python3
"""
Migration SQL pura senza SQLAlchemy
"""

import os
import subprocess

def run_sql_command(sql):
    """Esegue comando SQL diretto con psql"""
    try:
        result = subprocess.run([
            'psql', 
            '-h', 'localhost',
            '-U', 'intelligence_user', 
            '-d', 'intelligence',
            '-c', sql
        ], 
        capture_output=True, 
        text=True,
        env={**os.environ, 'PGPASSWORD': 'intelligence_pass'}
        )
        
        if result.returncode == 0:
            print(f"✅ {sql[:50]}...")
        else:
            print(f"❌ {sql[:50]}... | Error: {result.stderr}")
            
    except Exception as e:
        print(f"❌ {sql[:50]}... | Exception: {e}")

def main():
    print("🚀 Starting SQL migration...")
    
    migrations = [
        # Partner fields
        "ALTER TABLE companies ADD COLUMN IF NOT EXISTS is_partner BOOLEAN DEFAULT FALSE;",
        "ALTER TABLE companies ADD COLUMN IF NOT EXISTS is_supplier BOOLEAN DEFAULT FALSE;", 
        "ALTER TABLE companies ADD COLUMN IF NOT EXISTS partner_category VARCHAR(100);",
        "ALTER TABLE companies ADD COLUMN IF NOT EXISTS partner_description TEXT;",
        "ALTER TABLE companies ADD COLUMN IF NOT EXISTS partner_expertise JSONB DEFAULT '[]';",
        "ALTER TABLE companies ADD COLUMN IF NOT EXISTS partner_rating FLOAT DEFAULT 0.0;",
        "ALTER TABLE companies ADD COLUMN IF NOT EXISTS partner_status VARCHAR(50) DEFAULT 'active';",
        
        # Scraping fields
        "ALTER TABLE companies ADD COLUMN IF NOT EXISTS last_scraped_at TIMESTAMP;",
        "ALTER TABLE companies ADD COLUMN IF NOT EXISTS scraping_status VARCHAR(50) DEFAULT 'pending';",
        "ALTER TABLE companies ADD COLUMN IF NOT EXISTS ai_analysis_summary TEXT;",
        
        # Indexes
        "CREATE INDEX IF NOT EXISTS idx_companies_is_partner ON companies(is_partner);",
        "CREATE INDEX IF NOT EXISTS idx_companies_is_supplier ON companies(is_supplier);",
        "CREATE INDEX IF NOT EXISTS idx_companies_partner_category ON companies(partner_category);",
    ]
    
    for sql in migrations:
        run_sql_command(sql)
    
    # Verify result
    run_sql_command("SELECT COUNT(*) as total_companies FROM companies;")
    run_sql_command("SELECT COUNT(*) as companies_with_partner_field FROM companies WHERE is_partner IS NOT NULL;")
    
    print("🎉 Migration completed!")

if __name__ == "__main__":
    main()
