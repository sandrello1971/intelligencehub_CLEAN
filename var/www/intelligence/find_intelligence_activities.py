#!/usr/bin/env python3

import sys
sys.path.append('/var/www/intelligence')

from backend.app.services.crm.activities_sync import CRMSyncService

def find_intelligence():
    print("🎯 Searching for Intelligence activities...")
    
    with CRMSyncService() as sync_service:
        sync_service.get_crm_token() 
        sync_service.load_kit_names()
        
        activity_ids = sync_service.get_activities_ids(limit=100)
        print(f"📋 Checking {len(activity_ids)} activities for Intelligence type...")
        
        intelligence_found = 0
        
        for i, activity_id in enumerate(activity_ids[:50]):  # Check first 50
            try:
                activity = sync_service.get_activity_detail(activity_id)
                subtype = activity.get("subTypeId", "N/A")
                
                if subtype == 63705:  # Intelligence
                    intelligence_found += 1
                    description = activity.get("description", "")
                    subject = activity.get("subject", "")
                    
                    print(f"🎯 FOUND Intelligence Activity {activity_id}:")
                    print(f"   Subject: {subject}")
                    print(f"   Description: {description[:200]}...")
                    
                    kit_found = sync_service.find_kit_in_description(description)
                    print(f"   Kit detected: {kit_found}")
                    print("   ---")
                    
                    if intelligence_found >= 3:  # Stop after finding 3
                        break
                        
                elif i % 10 == 0:  # Progress every 10
                    print(f"   📊 Checked {i+1}/50 activities...")
                    
            except Exception as e:
                print(f"   ❌ Error with activity {activity_id}: {e}")
        
        print(f"🏁 Found {intelligence_found} Intelligence activities in first 50")

if __name__ == "__main__":
    find_intelligence()
