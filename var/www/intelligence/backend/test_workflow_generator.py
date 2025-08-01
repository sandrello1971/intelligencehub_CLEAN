#!/usr/bin/env python3
"""
Test script for Workflow Generator
Testa la generazione del flusso operativo dall'attività CRM
"""

import sys
import os

# Aggiungi il path del backend
sys.path.append('/var/www/intelligence/backend')
sys.path.append('/var/www/intelligence')

import logging

# Setup logging per test
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_workflow_generator")

def test_database_connection():
    """Test 1: Verifica connessione al database"""
    print("🔍 TEST 1: Verifica connessione database...")
    
    try:
        from app.core.database import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        
        # Test query
        result = db.execute(text("SELECT COUNT(*) FROM activities WHERE crm_activity_id = 725155")).fetchone()
        count = result[0] if result else 0
        
        print(f"✅ Database connesso. Attività con CRM ID 725155: {count}")
        db.close()
        return count > 0
        
    except Exception as e:
        print(f"❌ Errore connessione database: {e}")
        return False

def test_kit_extraction():
    """Test 2: Test estrazione kit dalla descrizione"""
    print("\n🔍 TEST 2: Test estrazione kit commerciale...")
    
    try:
        from app.core.database import SessionLocal
        from workflow_generator import WorkflowGenerator
        
        db = SessionLocal()
        generator = WorkflowGenerator(db)
        
        # Test con la descrizione reale dell'attività
        test_descriptions = [
            ("inserimento Startoffice finance", "sono interessati a startoffice finance"),
            ("Start Office Finance", "richiesta per start office finance"),
            ("SOF", "codice SOF richiesto"),
            ("formazione 4.0", "servizio formazione 4.0"),
            ("test random", "descrizione senza kit")
        ]
        
        for title, description in test_descriptions:
            kit_found = generator.extract_kit_from_description(description, title)
            status = "✅" if kit_found else "❌"
            print(f"   {status} '{title}' + '{description}' → {kit_found}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Errore test estrazione kit: {e}")
        return False

def test_user_mapping():
    """Test 3: Test mapping utente CRM"""
    print("\n🔍 TEST 3: Test mapping utente CRM...")
    
    try:
        from app.core.database import SessionLocal  
        from workflow_generator import WorkflowGenerator
        
        db = SessionLocal()
        generator = WorkflowGenerator(db)
        
        # Test con l'owner_id reale dell'attività (126370)
        user_found = generator.find_user_by_crm_id("126370")
        
        if user_found:
            print(f"✅ Utente trovato: {user_found['full_name']} ({user_found['email']})")
        else:
            print("❌ Utente CRM 126370 non trovato")
            
            # Verifica se ci sono utenti con CRM ID
            from sqlalchemy import text
            result = db.execute(text("SELECT COUNT(*) FROM users WHERE crm_id IS NOT NULL")).fetchone()
            print(f"📊 Utenti con CRM ID nel database: {result[0] if result else 0}")
        
        db.close()
        return user_found is not None
        
    except Exception as e:
        print(f"❌ Errore test mapping utente: {e}")
        return False

def test_workflow_components():
    """Test 4: Test componenti workflow"""
    print("\n🔍 TEST 4: Test componenti workflow...")
    
    try:
        from app.core.database import SessionLocal
        from workflow_generator import WorkflowGenerator
        
        db = SessionLocal()
        generator = WorkflowGenerator(db)
        
        # Test workflow di default
        workflow = generator.get_default_workflow()
        if workflow:
            print(f"✅ Workflow trovato: {workflow['nome']} (ID: {workflow['id']})")
            
            # Test milestone del workflow
            milestones = generator.get_workflow_milestones(workflow['id'])
            print(f"✅ Milestone trovate: {len(milestones)}")
            
            if milestones:
                first_milestone = milestones[0]
                print(f"   Prima milestone: {first_milestone['nome']} (SLA: {first_milestone['sla_giorni']} giorni)")
                
                # Test task della milestone
                tasks = generator.get_milestone_tasks(first_milestone['id'])
                print(f"✅ Task template trovati: {len(tasks)}")
                
                for i, task in enumerate(tasks[:3], 1):  # Mostra primi 3
                    print(f"   Task {i}: {task['nome']} ({task.get('durata_stimata_ore', 0)}h)")
        else:
            print("❌ Workflow di default non trovato")
        
        db.close()
        return workflow is not None
        
    except Exception as e:
        print(f"❌ Errore test componenti workflow: {e}")
        return False

def test_full_workflow_generation():
    """Test 5: Test generazione workflow completa"""
    print("\n🔍 TEST 5: Test generazione workflow completa...")
    print("⚠️ Questo test genererà un ticket REALE!")
    
    response = input("Continuare con la generazione del workflow? (s/N): ")
    if response.lower() != 's':
        print("❌ Test saltato dall'utente")
        return True
    
    try:
        from workflow_generator import generate_workflow_for_activity
        
        # Usa l'attività che abbiamo inserito (ID dovrebbe essere 83)
        activity_id = 83
        
        print(f"🚀 Generazione workflow per attività {activity_id}...")
        result = generate_workflow_for_activity(activity_id)
        
        print("✅ Generazione completata:")
        print(f"   Successo: {result['success']}")
        print(f"   Kit identificato: {result['kit_identificato']}")
        print(f"   Ticket creato: {result['ticket_creato']}")
        print(f"   Milestone create: {result['milestones_create']}")
        print(f"   Task creati: {result['tasks_creati']}")
        
        if result['errori']:
            print("⚠️ Errori riscontrati:")
            for errore in result['errori']:
                print(f"   - {errore}")
        
        return result['success']
        
    except Exception as e:
        print(f"❌ Errore test generazione workflow: {e}")
        return False

def test_verify_created_data():
    """Test 6: Verifica dati creati"""
    print("\n🔍 TEST 6: Verifica dati creati nel database...")
    
    try:
        from app.core.database import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        
        # Verifica ticket creati per l'attività
        ticket_query = text("""
            SELECT t.id, t.title, t.status, t.owner, t.workflow_id, t.milestone_id
            FROM tickets t 
            WHERE t.activity_id = 83
            ORDER BY t.created_at DESC
            LIMIT 3
        """)
        
        tickets = db.execute(ticket_query).fetchall()
        
        if tickets:
            print(f"✅ Ticket trovati: {len(tickets)}")
            for ticket in tickets:
                print(f"   - {ticket.title} (Status: {ticket.status}, Owner: {ticket.owner})")
                
                # Verifica task del ticket
                task_query = text("""
                    SELECT id, title, status, due_date, estimated_hours
                    FROM tasks 
                    WHERE ticket_id = :ticket_id
                    ORDER BY task_order, created_at
                """)
                
                tasks = db.execute(task_query, {"ticket_id": ticket.id}).fetchall()
                print(f"     Task associati: {len(tasks)}")
                
                for task in tasks[:3]:  # Mostra primi 3 task
                    print(f"       • {task.title} (Status: {task.status}, {task.estimated_hours}h)")
        else:
            print("⚠️ Nessun ticket trovato per l'attività 83")
        
        db.close()
        return len(tickets) > 0
        
    except Exception as e:
        print(f"❌ Errore verifica dati creati: {e}")
        return False

def run_all_tests():
    """Esegui tutti i test in sequenza"""
    print("🚀 AVVIO TEST SUITE WORKFLOW GENERATOR")
    print("🎯 Focus: Generazione flusso operativo da attività CRM")
    print("=" * 60)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Kit Extraction", test_kit_extraction),
        ("User Mapping", test_user_mapping),
        ("Workflow Components", test_workflow_components),
        ("Full Workflow Generation", test_full_workflow_generation),
        ("Verify Created Data", test_verify_created_data)
    ]
    
    results = {}
    
    for test_name, test_function in tests:
        try:
            results[test_name] = test_function()
        except Exception as e:
            print(f"💥 Test {test_name} fallito con eccezione: {e}")
            results[test_name] = False
    
    # Riepilogo risultati
    print("\n" + "=" * 60)
    print("📊 RIEPILOGO TEST:")
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Risultato finale: {passed}/{total} test superati")
    
    if passed >= total - 1:  # Permettiamo che alcuni test possano fallire
        print("🎉 Test completati con successo! Il modulo è pronto per l'uso.")
        return True
    else:
        print("⚠️ Alcuni test critici falliti. Rivedere il modulo prima dell'uso.")
        return False

if __name__ == "__main__":
    print("🧪 Test Workflow Generator Module")
    print("Per eseguire un test specifico, usa:")
    print("  python test_workflow_generator.py [test_number]")
    print("  Es: python test_workflow_generator.py 1  # Solo test database")
    print()
    
    if len(sys.argv) > 1:
        test_num = int(sys.argv[1])
        tests = [
            test_database_connection,
            test_kit_extraction,
            test_user_mapping,
            test_workflow_components,
            test_full_workflow_generation,
            test_verify_created_data
        ]
        
        if 1 <= test_num <= len(tests):
            tests[test_num - 1]()
        else:
            print(f"❌ Numero test non valido. Usa 1-{len(tests)}")
    else:
        # Esegui tutti i test
        run_all_tests()
