#!/usr/bin/env python3
"""
Update companies from CRM - Enhanced version
"""

import sys
sys.path.append('/var/www/intelligence/backend')

from app.integrations.crm_incloud.companies_sync_simple import *

def main():
    print("🔄 Updating companies from CRM...")
    
    try:
        # Use existing CRM sync
        from app.integrations.crm_incloud.companies_sync_simple import sync_companies_safe
        result = sync_companies_safe(limit=50, dry_run=False)
        print(f"✅ Sync completed: {result}")
    except Exception as e:
        print(f"❌ CRM sync error: {e}")
        
        # Fallback: show current companies count
        try:
            engine = create_engine(DATABASE_URL)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM companies;"))
                count = result.fetchone()[0]
                print(f"📊 Current companies in DB: {count}")
        except Exception as db_error:
            print(f"❌ DB error: {db_error}")

if __name__ == "__main__":
    main()
