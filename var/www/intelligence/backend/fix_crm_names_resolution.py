#!/usr/bin/env python3
"""
Fix per risolvere i nomi da ID nel CRM
"""
import sys
sys.path.append('/var/www/intelligence/backend')
sys.path.append('/var/www/intelligence')

from crm_activities_sync import CRMActivitiesSync
from app.core.database import SessionLocal
import requests
import time

def get_owner_name(owner_id, token):
    """Recupera il nome del proprietario dall'ID"""
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "WebApiKey": "r5l50i5lvd.YjuIXg0PPJnqzeldzCBlEpMlwqJPRPFgJppSkPu"
        }
        
        # Prova diversi endpoint per gli utenti
        endpoints = [
            f"https://api.crmincloud.it/api/v1/User/{owner_id}",
            f"https://api.crmincloud.it/api/v1/Users/{owner_id}",
            f"https://api.crmincloud.it/api/v1/Contact/{owner_id}",
            f"https://api.crmincloud.it/api/v1/Contacts/{owner_id}"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    name = (data.get('name') or 
                           data.get('fullName') or 
                           data.get('displayName') or
                           f"{data.get('firstName', '')} {data.get('lastName', '')}".strip())
                    
                    if name:
                        print(f"✅ Owner {owner_id}: '{name}' (da {endpoint})")
                        return name
                        
            except Exception as e:
                continue
                
        print(f"⚠️ Nome owner {owner_id} non trovato")
        return ""
        
    except Exception as e:
        print(f"❌ Errore get_owner_name: {e}")
        return ""

def get_company_name(company_id, token):
    """Recupera il nome dell'azienda dall'ID"""
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "WebApiKey": "r5l50i5lvd.YjuIXg0PPJnqzeldzCBlEpMlwqJPRPFgJppSkPu"
        }
        
        # Prova diversi endpoint per le aziende
        endpoints = [
            f"https://api.crmincloud.it/api/v1/Company/{company_id}",
            f"https://api.crmincloud.it/api/v1/Companies/{company_id}",
            f"https://api.crmincloud.it/api/v1/Account/{company_id}",
            f"https://api.crmincloud.it/api/v1/Accounts/{company_id}"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    name = (data.get('companyName') or 
                           data.get('name') or 
                           data.get('displayName') or
                           data.get('businessName'))
                    
                    if name:
                        print(f"✅ Company {company_id}: '{name}' (da {endpoint})")
                        return name
                        
            except Exception as e:
                continue
                
        print(f"⚠️ Nome company {company_id} non trovato")
        return ""
        
    except Exception as e:
        print(f"❌ Errore get_company_name: {e}")
        return ""

def fix_activity_names():
    """Fix dei nomi per l'attività problematica"""
    try:
        db = SessionLocal()
        sync_service = CRMActivitiesSync(db)
        token = sync_service.get_crm_token()
        
        # Test con l'attività problematica
        owner_id = "126370"
        company_id = "1740449"
        
        print("🔍 RISOLUZIONE NOMI:")
        print("=" * 40)
        
        owner_name = get_owner_name(owner_id, token)
        time.sleep(1)  # Rate limiting
        company_name = get_company_name(company_id, token)
        
        print(f"\n📋 RISULTATI:")
        print(f"  Owner ID {owner_id} → '{owner_name}'")
        print(f"  Company ID {company_id} → '{company_name}'")
        
        if owner_name or company_name:
            # Aggiorna l'attività nel database
            from sqlalchemy import text
            
            update_query = text("""
                UPDATE activities 
                SET owner_name = :owner_name,
                    customer_name = :customer_name
                WHERE crm_activity_id = 724246
            """)
            
            db.execute(update_query, {
                'owner_name': owner_name,
                'customer_name': company_name
            })
            
            db.commit()
            print(f"\n✅ Attività 724246 aggiornata nel database!")
            print("🔍 Controlla ora il ticket nell'interfaccia web!")
            
        db.close()
        
    except Exception as e:
        print(f"❌ Errore fix: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_activity_names()
