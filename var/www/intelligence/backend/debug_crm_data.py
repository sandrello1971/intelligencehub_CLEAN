#!/usr/bin/env python3
"""
Debug per vedere esattamente cosa arriva dal CRM
"""
import sys
sys.path.append('/var/www/intelligence/backend')
sys.path.append('/var/www/intelligence')

from crm_activities_sync import CRMActivitiesSync
from app.core.database import SessionLocal
import requests

def debug_crm_activity(crm_activity_id):
    """Debug di un'attività specifica dal CRM"""
    try:
        db = SessionLocal()
        sync_service = CRMActivitiesSync(db)
        token = sync_service.get_crm_token()
        
        headers = {
            "Authorization": f"Bearer {token}",
            "WebApiKey": "r5l50i5lvd.YjuIXg0PPJnqzeldzCBlEpMlwqJPRPFgJppSkPu"
        }
        
        # Leggi attività dal CRM
        url = f"https://api.crmincloud.it/api/v1/Activity/{crm_activity_id}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            crm_data = response.json()
            
            print(f"📡 DATI RAW DAL CRM - Attività {crm_activity_id}:")
            print("=" * 60)
            
            # Campi che ci interessano
            important_fields = [
                'id', 'ownerName', 'ownerId', 'companyName', 'companyId', 
                'customerName', 'customerId', 'accountName', 'client',
                'assignedTo', 'responsible', 'title', 'description'
            ]
            
            print("🔍 CAMPI IMPORTANTI:")
            for field in important_fields:
                value = crm_data.get(field, "NON_PRESENTE")
                print(f"  {field}: '{value}'")
            
            print(f"\n📋 TUTTI I CAMPI DISPONIBILI:")
            for key, value in sorted(crm_data.items()):
                print(f"  {key}: '{value}'")
                
            # Test del mapping
            print(f"\n🔄 TEST MAPPING:")
            mapped_data = sync_service.map_crm_activity_to_local(crm_data)
            print(f"  owner_name mappato: '{mapped_data.get('owner_name', '')}'")
            print(f"  customer_name mappato: '{mapped_data.get('customer_name', '')}'")
            
        else:
            print(f"❌ Errore lettura CRM: {response.status_code} - {response.text}")
            
        db.close()
        
    except Exception as e:
        print(f"❌ Errore debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Debug dell'attività problematica
    debug_crm_activity(724246)
