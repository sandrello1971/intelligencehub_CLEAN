#!/usr/bin/env python3

import sys
sys.path.append('/var/www/intelligence')

from backend.app.services.crm.activities_sync import CRMSyncService

def quick_test():
    print("🚀 Quick CRM Test...")
    
    with CRMSyncService() as sync_service:
        # Setup
        sync_service.get_crm_token() 
        sync_service.load_kit_names()
        
        # Test solo le prime 3 attività
        activity_ids = sync_service.get_activities_ids(limit=100)
        print(f"📋 Got {len(activity_ids)} IDs")
        
        # Processa solo le prime 3
        for i, activity_id in enumerate(activity_ids[:3]):
            print(f"🔍 Processing activity {i+1}/3: {activity_id}")
            
            try:
                activity = sync_service.get_activity_detail(activity_id)
                subtype = activity.get("subTypeId", "N/A")
                is_intel = subtype == 63705
                
                print(f"   SubType: {subtype}, Intelligence: {is_intel}")
                
                if is_intel:
                    description = activity.get("description", "")
                    print(f"   Description: {description[:100]}...")
                    
                    kit_found = sync_service.find_kit_in_description(description)
                    print(f"   Kit found: {kit_found}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    quick_test()
