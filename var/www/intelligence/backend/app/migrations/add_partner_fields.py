#!/usr/bin/env python3
"""
Migration: Add Partner/Supplier fields to existing companies table
"""

import os
import sys
sys.path.append('/var/www/intelligence/backend')

from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://intelligence_user:intelligence_pass@localhost/intelligence"

def run_migration():
    engine = create_engine(DATABASE_URL)
    
    migrations = [
        # Partner/Supplier management
        "ALTER TABLE companies ADD COLUMN IF NOT EXISTS is_partner BOOLEAN DEFAULT FALSE;",
        "ALTER TABLE companies ADD COLUMN IF NOT EXISTS is_supplier BOOLEAN DEFAULT FALSE;", 
        "ALTER TABLE companies ADD COLUMN IF NOT EXISTS partner_category VARCHAR(100);",
        "ALTER TABLE companies ADD COLUMN IF NOT EXISTS partner_description TEXT;",
        "ALTER TABLE companies ADD COLUMN IF NOT EXISTS partner_expertise JSONB DEFAULT '[]';",
        "ALTER TABLE companies ADD COLUMN IF NOT EXISTS partner_rating FLOAT DEFAULT 0.0;",
        "ALTER TABLE companies ADD COLUMN IF NOT EXISTS partner_status VARCHAR(50) DEFAULT 'active';",
        
        # Scraping status tracking
        "ALTER TABLE companies ADD COLUMN IF NOT EXISTS last_scraped_at TIMESTAMP;",
        "ALTER TABLE companies ADD COLUMN IF NOT EXISTS scraping_status VARCHAR(50) DEFAULT 'pending';",
        "ALTER TABLE companies ADD COLUMN IF NOT EXISTS ai_analysis_summary TEXT;",
        
        # Indexes for performance
        "CREATE INDEX IF NOT EXISTS idx_companies_is_partner ON companies(is_partner);",
        "CREATE INDEX IF NOT EXISTS idx_companies_is_supplier ON companies(is_supplier);",
        "CREATE INDEX IF NOT EXISTS idx_companies_partner_category ON companies(partner_category);",
        "CREATE INDEX IF NOT EXISTS idx_companies_sito_web ON companies(sito_web);",
        "CREATE INDEX IF NOT EXISTS idx_companies_settore ON companies(settore);",
    ]
    
    with engine.connect() as conn:
        for migration in migrations:
            try:
                conn.execute(text(migration))
                print(f"✅ {migration}")
            except Exception as e:
                print(f"❌ {migration} - Error: {e}")
        
        conn.commit()
    
    print("🎉 Migration completed!")

if __name__ == "__main__":
    run_migration()
