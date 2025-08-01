#!/usr/bin/env python3
"""
CRM Update Module - Aggiorna attività sul CRM
"""

import os
import logging
import requests
import time
from datetime import datetime
from typing import Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crm_update")

# Configurazione CRM da variabili ambiente o config
def get_crm_config():
    """Recupera configurazione CRM da environment o config"""
    try:
        # Prova prima dalle variabili ambiente
        api_key = os.getenv('CRM_API_KEY')
        username = os.getenv('CRM_USERNAME') 
        password = os.getenv('CRM_PASSWORD')
        base_url = os.getenv('CRM_BASE_URL')
        
        # Se non presenti, prova a importare dalla config esistente
        if not all([api_key, username, password, base_url]):
            try:
                # Import dalla config del sync esistente
                import sys
                sys.path.append('/var/www/intelligence')
                from crm_activities_sync import CRM_API_KEY, CRM_USERNAME, CRM_PASSWORD, CRM_BASE_URL
                
                api_key = CRM_API_KEY
                username = CRM_USERNAME
                password = CRM_PASSWORD
                base_url = CRM_BASE_URL
                
            except ImportError:
                logger.error("❌ Configurazione CRM non trovata né in ENV né in config file")
                raise
        
        return {
            'api_key': api_key,
            'username': username,
            'password': password,
            'base_url': base_url
        }
        
    except Exception as e:
        logger.error(f"❌ Errore caricamento config CRM: {e}")
        raise

# Rate limiting
MAX_CALLS_PER_MINUTE = 45
last_request_time = 0

def rate_limited_request(url: str, headers: dict, method: str = "GET", data: dict = None):
    """Rate limited request con retry"""
    global last_request_time
    
    # Rate limiting
    current_time = time.time()
    time_since_last = current_time - last_request_time
    min_interval = 60.0 / MAX_CALLS_PER_MINUTE
    
    if time_since_last < min_interval:
        sleep_time = min_interval - time_since_last
        time.sleep(sleep_time)
    
    last_request_time = time.time()
    
    # Esegui richiesta
    try:
        if method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=30)
        elif method.upper() == "PATCH":
            response = requests.patch(url, headers=headers, json=data, timeout=30)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=30)
        else:
            response = requests.get(url, headers=headers, timeout=30)
        
        response.raise_for_status()
        return response
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Errore richiesta CRM: {e}")
        raise

def get_crm_token():
    """Ottiene token CRM usando il metodo che funziona"""
    try:
        import sys
        sys.path.append("/var/www/intelligence")
        sys.path.append("/var/www/intelligence/backend")
        
        from crm_activities_sync import CRMActivitiesSync
        from app.core.database import SessionLocal
        
        db = SessionLocal()
        try:
            sync_service = CRMActivitiesSync(db)
            token = sync_service.get_crm_token()
            
            if not token:
                raise Exception("Token non ricevuto dal CRM")
            
            logger.info("🔐 Token CRM ottenuto con successo")
            return token
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"❌ Errore autenticazione CRM: {e}")
        raise

def update_activity_description(crm_activity_id: str, ticket_code: str, customer_care_message: str = None) -> bool:
    """
    Aggiorna la descrizione di un'attività CRM aggiungendo info sul ticket
    
    Args:
        crm_activity_id: ID dell'attività sul CRM
        ticket_code: Codice del ticket generato (es: TCK-SOF-5155-00)
        customer_care_message: Messaggio personalizzato (opzionale)
    
    Returns:
        bool: True se aggiornamento riuscito, False altrimenti
    """
    try:
        logger.info(f"🔄 Aggiornamento attività CRM {crm_activity_id} con ticket {ticket_code}")
        
        # Ottieni configurazione e token
        config = get_crm_config()
        # SEMPRE rigenerare il token - non cachare mai
        token = get_crm_token()
        
        headers = {
            "Authorization": f"Bearer {token}",
            "WebApiKey": config['api_key'],
            "Content-Type": "application/json"
        }
        
        # Prima recupera l'attività corrente per ottenere la descrizione esistente
        get_url = f"{config['base_url']}/api/v1/Activity/{crm_activity_id}"
        logger.info(f"📡 Recupero attività corrente: {get_url}")
        
        response = rate_limited_request(get_url, headers)
        activity_data = response.json()
        
        current_description = activity_data.get("description", "")
        logger.info(f"📝 Descrizione corrente: {current_description[:100]}...")
        
        # Prepara il messaggio da aggiungere
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        if customer_care_message:
            update_message = customer_care_message
        else:
            update_message = f"""

--- CUSTOMER CARE INTELLIGENCE ---
✅ Attività presa in carico automaticamente
🎫 Ticket: {ticket_code}
📅 Data: {timestamp}
🔗 Sistema: Intelligence Workflow
-----------------------------------"""
        
        # Nuova descrizione = descrizione esistente + messaggio
        new_description = current_description + update_message
        
        # Prepara dati per l'update
        update_data = {
            "description": new_description
        }
        
        # Esegui update
        update_url = f"{config['base_url']}/api/v1/Activity/{crm_activity_id}"
        logger.info(f"🔄 Invio update: {update_url}")
        
        response = rate_limited_request(update_url, headers, method="PUT", data=update_data)
        
        if response.status_code in [200, 204]:
            logger.info(f"✅ Attività CRM {crm_activity_id} aggiornata con successo")
            return True
        else:
            logger.error(f"❌ Update fallito: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Errore aggiornamento attività CRM {crm_activity_id}: {e}")
        return False

def test_crm_update():
    """Test della funzione di update"""
    # Trova un'attività di test
    try:
        import sys
        sys.path.append("/var/www/intelligence/backend")
        from app.core.database import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        result = db.execute(text("""
            SELECT crm_activity_id 
            FROM activities 
            WHERE crm_activity_id IS NOT NULL 
            ORDER BY created_at DESC 
            LIMIT 1
        """)).fetchone()
        
        if result:
            test_crm_id = result[0]
            logger.info(f"🧪 Test update su attività CRM {test_crm_id}")
            
            success = update_activity_description(
                crm_activity_id=str(test_crm_id),
                ticket_code="TCK-TEST-0000-00",
                customer_care_message="\n--- TEST CUSTOMER CARE ---\n✅ Test aggiornamento automatico\n📅 " + datetime.now().strftime("%d/%m/%Y %H:%M") + "\n-------------------------"
            )
            
            if success:
                logger.info("🎉 Test update CRM completato con successo!")
            else:
                logger.error("❌ Test update CRM fallito")
                
        else:
            logger.warning("⚠️ Nessuna attività CRM trovata per il test")
            
        db.close()
        
    except Exception as e:
        logger.error(f"❌ Errore test: {e}")

if __name__ == "__main__":
    test_crm_update()

def update_activity_task_status(crm_activity_id: str, ticket_code: str, task_name: str, old_status: str, new_status: str) -> bool:
    """
    Aggiorna attività CRM quando cambia lo stato di un task
    """
    try:
        logger.info(f"🔄 Aggiornamento CRM - Task {task_name}: {old_status} → {new_status}")
        
        config = get_crm_config()
        # SEMPRE rigenerare il token - non cachare mai
        token = get_crm_token()
        
        headers = {
            "Authorization": f"Bearer {token}",
            "WebApiKey": config['api_key'],
            "Content-Type": "application/json"
        }
        
        # Recupera descrizione corrente
        get_url = f"{config['base_url']}/api/v1/Activity/{crm_activity_id}"
        response = rate_limited_request(get_url, headers)
        activity_data = response.json()
        current_description = activity_data.get("description", "")
        
        # Prepara messaggio aggiornamento task
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        status_emoji = {
            "todo": "📋",
            "in_progress": "⚡", 
            "completed": "✅",
            "suspended": "⏸️",
            "cancelled": "❌"
        }
        
        update_message = f"""
🔄 [{timestamp}] Task: {task_name}
   {status_emoji.get(old_status, '📋')} {old_status} → {status_emoji.get(new_status, '📋')} {new_status}
   🎫 Ticket: {ticket_code}"""
        
        new_description = current_description + update_message
        
        # Aggiorna CRM
        update_data = {
            "id": crm_activity_id,
            "description": new_description
        }
        
        update_url = f"{config['base_url']}/api/v1/Activity"
        response = rate_limited_request(update_url, headers, method="POST", data=update_data)
        
        if response.status_code == 200:
            logger.info(f"✅ CRM aggiornato - Task {task_name} → {new_status}")
            return True
        else:
            logger.error(f"❌ Update CRM fallito: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Errore aggiornamento task CRM: {e}")
        return False

def update_activity_ticket_closed(crm_activity_id: str, ticket_code: str, total_tasks: int, completed_tasks: int) -> bool:
    """
    Aggiorna attività CRM quando il ticket viene chiuso (tutti i task completati)
    """
    try:
        logger.info(f"🎯 Chiusura ticket {ticket_code} - {completed_tasks}/{total_tasks} task completati")
        
        config = get_crm_config()
        # SEMPRE rigenerare il token - non cachare mai
        token = get_crm_token()
        
        headers = {
            "Authorization": f"Bearer {token}",
            "WebApiKey": config['api_key'],
            "Content-Type": "application/json"
        }
        
        # Recupera descrizione corrente
        get_url = f"{config['base_url']}/api/v1/Activity/{crm_activity_id}"
        response = rate_limited_request(get_url, headers)
        activity_data = response.json()
        current_description = activity_data.get("description", "")
        
        # Messaggio di chiusura ticket
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        closure_message = f"""

🎉 [TICKET COMPLETATO] {timestamp}
✅ Ticket: {ticket_code} - FASE 1 COMPLETATA
📊 Task completati: {completed_tasks}/{total_tasks}
🚀 Avvio automatico FASE 2
-----------------------------------"""
        
        new_description = current_description + closure_message
        
        # Aggiorna CRM
        update_data = {
            "id": crm_activity_id,
            "description": new_description
        }
        
        update_url = f"{config['base_url']}/api/v1/Activity"
        response = rate_limited_request(update_url, headers, method="POST", data=update_data)
        
        if response.status_code == 200:
            logger.info(f"✅ CRM aggiornato - Ticket {ticket_code} chiuso")
            return True
        else:
            logger.error(f"❌ Update CRM fallito: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Errore chiusura ticket CRM: {e}")
        return False

def close_activity_on_crm(crm_activity_id: str, ticket_code: str) -> bool:
    """
    Chiude definitivamente l'attività sul CRM
    """
    try:
        logger.info(f"🏁 Chiusura definitiva attività CRM {crm_activity_id}")
        
        config = get_crm_config()
        # SEMPRE rigenerare il token - non cachare mai
        token = get_crm_token()
        
        headers = {
            "Authorization": f"Bearer {token}",
            "WebApiKey": config['api_key'],
            "Content-Type": "application/json"
        }
        
        # Prima aggiorna la descrizione con messaggio finale
        get_url = f"{config['base_url']}/api/v1/Activity/{crm_activity_id}"
        response = rate_limited_request(get_url, headers)
        activity_data = response.json()
        current_description = activity_data.get("description", "")
        
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        final_message = f"""

🏁 [ATTIVITÀ COMPLETATA] {timestamp}
✅ Ticket: {ticket_code} - TUTTE LE FASI COMPLETATE
🎯 Workflow Intelligence completato con successo
-----------------------------------"""
        
        final_description = current_description + final_message
        
        # Aggiorna descrizione e chiudi attività
        close_data = {
            "id": crm_activity_id,
            "description": final_description,
            "status": "completed"  # O il valore corretto per "completata"
        }
        
        update_url = f"{config['base_url']}/api/v1/Activity"
        response = rate_limited_request(update_url, headers, method="POST", data=close_data)
        
        if response.status_code == 200:
            logger.info(f"🏁 Attività CRM {crm_activity_id} chiusa definitivamente")
            return True
        else:
            logger.error(f"❌ Chiusura attività CRM fallita: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Errore chiusura attività CRM: {e}")
        return False
