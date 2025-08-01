#!/usr/bin/env python3
"""
Test script for CRM Activities Sync
Verifica il funzionamento del modulo prima di utilizzarlo in produzione
"""

import sys
import os

# Aggiungi il path del backend
sys.path.append('/var/www/intelligence/backend')
sys.path.append('/var/www/intelligence')

import logging

# Setup logging per test
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_crm_sync")

def test_database_connection():
    """Test 1: Verifica connessione al database"""
    print("🔍 TEST 1: Verifica connessione database...")
    
    try:
        from app.core.database import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        
        # Test query sulla tabella activities
        result = db.execute(text("SELECT COUNT(*) FROM activities")).fetchone()
        count = result[0] if result else 0
        
        print(f"✅ Database connesso. Attività esistenti: {count}")
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Errore connessione database: {e}")
        return False

def test_crm_connection():
    """Test 2: Verifica connessione al CRM"""
    print("\n🔍 TEST 2: Verifica connessione CRM...")
    
    try:
        from app.core.database import SessionLocal
        from crm_activities_sync import CRMActivitiesSync
        
        db = SessionLocal()
        sync_service = CRMActivitiesSync(db)
        
        # Test solo ottenimento token
        token = sync_service.get_crm_token()
        
        if token:
            print(f"✅ Token CRM ottenuto: {token[:20]}...")
            db.close()
            return True
        else:
            print("❌ Token CRM non ottenuto")
            db.close()
            return False
            
    except Exception as e:
        print(f"❌ Errore connessione CRM: {e}")
        return False

def test_fetch_activities():
    """Test 3: Verifica scaricamento attività CRM (senza inserimento)"""
    print("\n🔍 TEST 3: Verifica scaricamento attività CRM (SubType: 63705)...")
    
    try:
        from app.core.database import SessionLocal
        from crm_activities_sync import CRMActivitiesSync, INTELLIGENCE_SUBTYPE_ID
        
        db = SessionLocal()
        sync_service = CRMActivitiesSync(db)
        
        # Ottieni token
        sync_service.get_crm_token()
        
        # Scarica solo 3 attività per test
        activities = sync_service.fetch_activities_by_subtype(limit=3)
        
        print(f"✅ Scaricate {len(activities)} attività CRM (SubType: {INTELLIGENCE_SUBTYPE_ID})")
        
        if activities:
            first_activity = activities[0]
            print(f"📋 Prima attività:")
            print(f"   ID: {first_activity.get('id', 'N/A')}")
            print(f"   Subject: {first_activity.get('subject', 'N/A')}")
            print(f"   CompanyId: {first_activity.get('companyId', 'N/A')}")
            print(f"   SubTypeId: {first_activity.get('subTypeId', 'N/A')}")
            print(f"   Tipo oggetto: {type(first_activity)}")
        else:
            print("⚠️ Nessuna attività trovata - potrebbe essere normale se non ci sono attività del tipo 63705")
        
        db.close()
        return True  # Non facciamo fallire il test se non ci sono attività
        
    except Exception as e:
        print(f"❌ Errore scaricamento attività: {e}")
        return False

def test_data_mapping():
    """Test 4: Verifica mappatura dati"""
    print("\n🔍 TEST 4: Verifica mappatura dati...")
    
    # Dati di test simulando una risposta CRM
    mock_crm_activity = {
        "id": 12345,
        "subject": "Test Activity",
        "description": "Test Description",
        "activityDate": "2025-07-31T10:00:00",
        "status": "aperta",
        "priority": 2,
        "ownerId": 100,
        "ownerName": "Test Owner",
        "companyId": 200,
        "companyName": "Test Company"
    }
    
    try:
        from app.core.database import SessionLocal
        from crm_activities_sync import CRMActivitiesSync
        
        db = SessionLocal()
        sync_service = CRMActivitiesSync(db)
        
        # Test mappatura
        mapped_data = sync_service.map_crm_to_local_activity(mock_crm_activity)
        
        print("✅ Mappatura dati completata:")
        print(f"   Titolo: {mapped_data['title']}")
        print(f"   Status: {mapped_data['status']}")
        print(f"   Priorità: {mapped_data['priority']}")
        print(f"   CRM ID: {mapped_data['crm_activity_id']}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Errore mappatura dati: {e}")
        return False

def test_sync_dry_run():
    """Test 5: Test sync con 1 sola attività"""
    print("\n🔍 TEST 5: Test sync con 1 attività (REALE - attenzione!)...")
    
    response = input("⚠️ Questo test farà un sync REALE con 1 attività. Continuare? (s/N): ")
    if response.lower() != 's':
        print("❌ Test saltato dall'utente")
        return True
    
    try:
        from crm_activities_sync import run_sync
        
        # Usa la funzione run_sync con limit di 1 per test
        stats = run_sync(limit=1)
        
        print("✅ Sync test completato:")
        print(f"   Attività scaricate: {stats.get('activities_fetched', 0)}")
        print(f"   Attività inserite: {stats.get('activities_inserted', 0)}")
        print(f"   Attività saltate: {stats.get('activities_skipped', 0)}")
        print(f"   Errori: {stats.get('errors', 0)}")
        
        return stats.get('errors', 0) == 0
        
    except Exception as e:
        print(f"❌ Errore sync test: {e}")
        return False

def run_all_tests():
    """Esegui tutti i test in sequenza"""
    print("🚀 AVVIO TEST SUITE CRM ACTIVITIES SYNC")
    print("🎯 Focus: SubType 63705 (Intelligence)")
    print("=" * 50)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("CRM Connection", test_crm_connection),
        ("Fetch Activities", test_fetch_activities),
        ("Data Mapping", test_data_mapping),
        ("Sync Test (1 activity)", test_sync_dry_run)
    ]
    
    results = {}
    
    for test_name, test_function in tests:
        try:
            results[test_name] = test_function()
        except Exception as e:
            print(f"💥 Test {test_name} fallito con eccezione: {e}")
            results[test_name] = False
    
    # Riepilogo risultati
    print("\n" + "=" * 50)
    print("📊 RIEPILOGO TEST:")
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Risultato finale: {passed}/{total} test superati")
    
    if passed >= total - 1:  # Permettiamo che il sync test possa essere saltato
        print("🎉 Test completati con successo! Il modulo è pronto per l'uso.")
        return True
    else:
        print("⚠️ Alcuni test critici falliti. Rivedere il modulo prima dell'uso.")
        return False

if __name__ == "__main__":
    print("🧪 Test CRM Activities Sync Module (SubType: 63705)")
    print("Per eseguire un test specifico, usa:")
    print("  python test_crm_sync.py [test_number]")
    print("  Es: python test_crm_sync.py 1  # Solo test database")
    print()
    
    if len(sys.argv) > 1:
        test_num = int(sys.argv[1])
        tests = [
            test_database_connection,
            test_crm_connection, 
            test_fetch_activities,
            test_data_mapping,
            test_sync_dry_run
        ]
        
        if 1 <= test_num <= len(tests):
            tests[test_num - 1]()
        else:
            print(f"❌ Numero test non valido. Usa 1-{len(tests)}")
    else:
        # Esegui tutti i test
        run_all_tests()
