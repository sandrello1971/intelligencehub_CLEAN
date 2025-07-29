#!/usr/bin/env python3

import sys
import os
sys.path.append('/var/www/intelligence')

# Import con path corretto
from backend.app.services.crm.activities_sync import CRMSyncService

def test_sync():
    print("🚀 Testing CRM Sync...")
    
    with CRMSyncService() as sync_service:
        # Test solo connessione e caricamento kit
        try:
            sync_service.get_crm_token()
            print("✅ CRM connection OK")
            
            kit_names = sync_service.load_kit_names()
            print(f"✅ Loaded {len(kit_names)} kit names")
            
            # Test con 5 attività
            stats = sync_service.sync_activities(limit=5)
            print(f"📊 Results: {stats}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_sync()
