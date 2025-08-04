#!/usr/bin/env python3
"""
CRM Activities Sync - Modulo Base v1.0 - FILTRO CLIENT-SIDE
Sincronizza SOLO le attività del tipo 63705 dal CRM alla tabella activities locale
"""

import os
import time
import logging
import requests
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crm_activities_sync")

# Configurazione CRM
CRM_API_KEY = "r5l50i5lvd.YjuIXg0PPJnqzeldzCBlEpMlwqJPRPFgJppSkPu"
CRM_USERNAME = "intellivoice@enduser-digital.com"
CRM_PASSWORD = "B4b4in4_07"
CRM_BASE_URL = "https://api.crmincloud.it"

# SubType ID per attività Intelligence (CONFERMATO: 63705)
INTELLIGENCE_SUBTYPE_ID = 63705

# Rate limiting (45 chiamate al minuto)
MAX_CALLS_PER_MINUTE = 45
CALL_INTERVAL = 60 / MAX_CALLS_PER_MINUTE

class CRMActivitiesSync:
    """
    Sincronizzatore attività CRM Intelligence
    Focus: scaricare SOLO attività del tipo 63705 e salvarle nella tabella activities
    """
    
    def __init__(self, database_session: Session):
        self.db = database_session
        self.token = None
        self.headers = None
        
    def get_crm_token(self) -> str:
        """Ottieni token di autenticazione CRM"""
        url = f"{CRM_BASE_URL}/api/v1/Auth/Login"
        payload = {
            "grant_type": "password",
            "username": CRM_USERNAME,
            "password": CRM_PASSWORD
        }
        headers = {
            "WebApiKey": CRM_API_KEY,
            "Content-Type": "application/json"
        }
        
        logger.info("🔐 Richiesta token CRM...")
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        self.token = response.json()["access_token"]
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "WebApiKey": CRM_API_KEY,
            "Content-Type": "application/json"
        }
        
        logger.info("✅ Token CRM ottenuto")
        return self.token
    
    def rate_limited_request(self, url: str) -> requests.Response:
        """Esegui richiesta GET con rate limiting"""
        time.sleep(CALL_INTERVAL)
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response
    
    def fetch_activities_by_subtype(self, limit: int = 50) -> List[Dict]:
        """
        Scarica attività CRM e filtra per SubType 63705 CLIENT-SIDE
        
        Args:
            limit: Numero massimo di attività da scaricare
            
        Returns:
            Lista di attività CRM del tipo 63705
        """
        # Aumentiamo il limite per compensare il filtro client-side
        fetch_limit = min(limit * 5, 500)  # Scarica più attività per trovare quelle giuste
        
        # URL per ottenere attività CRM SENZA filtro (il filtro server non funziona)
        url = f"{CRM_BASE_URL}/api/v1/Activity?$top={fetch_limit}&$orderby=id desc"
        
        logger.info(f"📥 Scaricamento {fetch_limit} attività CRM per filtro client-side (SubType: {INTELLIGENCE_SUBTYPE_ID})...")
        
        try:
            response = self.rate_limited_request(url)
            data = response.json()
            
            # Debug: stampa la struttura della risposta
            logger.info(f"🔍 Tipo risposta CRM: {type(data)}")
            
            all_activities = []
            
            if isinstance(data, list):
                # Se è una lista di ID, dobbiamo fare richieste separate per ogni attività
                if data and isinstance(data[0], int):
                    logger.info(f"📋 Ricevuti {len(data)} ID attività, scarico dettagli...")
                    all_activities = self._fetch_activity_details(data)
                else:
                    # Se è già una lista di oggetti
                    all_activities = data
            elif isinstance(data, dict) and "value" in data:
                # Se è un wrapper con "value"
                if data["value"] and isinstance(data["value"][0], int):
                    logger.info(f"📋 Ricevuti {len(data['value'])} ID attività, scarico dettagli...")
                    all_activities = self._fetch_activity_details(data["value"])
                else:
                    all_activities = data["value"]
            else:
                logger.error(f"❌ Struttura risposta CRM non riconosciuta: {type(data)}")
                return []
            
            # FILTRO CLIENT-SIDE per SubType 63705
            filtered_activities = []
            for activity in all_activities:
                if isinstance(activity, dict) and activity.get("subTypeId") == INTELLIGENCE_SUBTYPE_ID:
                    filtered_activities.append(activity)
                    logger.info(f"✅ Attività {activity.get('id')} ha SubType {INTELLIGENCE_SUBTYPE_ID} - INCLUSA")
                elif isinstance(activity, dict):
                    logger.info(f"⏭️ Attività {activity.get('id')} ha SubType {activity.get('subTypeId')} - SALTATA")
            
            # Limita al numero richiesto
            result = filtered_activities[:limit]
            
            logger.info(f"✅ Trovate {len(filtered_activities)} attività con SubType {INTELLIGENCE_SUBTYPE_ID}, restituisco prime {len(result)}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Errore richiesta CRM: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Errore generico: {e}")
            return []
    
    def _fetch_activity_details(self, activity_ids: List[int]) -> List[Dict]:
        """
        Scarica i dettagli delle attività dato una lista di ID
        
        Args:
            activity_ids: Lista di ID attività CRM
            
        Returns:
            Lista di attività complete
        """
        activities = []
        
        for activity_id in activity_ids:
            try:
                url = f"{CRM_BASE_URL}/api/v1/Activity/{activity_id}/GetFull"
                response = self.rate_limited_request(url)
                activity_data = response.json()
                
                if isinstance(activity_data, dict):
                    activities.append(activity_data)
                    subtype = activity_data.get('subTypeId', 'N/A')
                    logger.info(f"📝 Scaricata attività {activity_id} (SubType: {subtype}): {activity_data.get('subject', 'N/A')}")
                else:
                    logger.warning(f"⚠️ Attività {activity_id} non ha formato valido")
                    
            except Exception as e:
                logger.error(f"❌ Errore scaricando attività {activity_id}: {e}")
                continue
        
        return activities
    
    def map_crm_to_local_activity(self, crm_activity: Dict) -> Dict:
        """
        Mappa i dati dell'attività CRM ai campi della tabella activities locale
        
        Args:
            crm_activity: Dati attività CRM
            
        Returns:
            Dizionario con i campi mappati per la tabella activities
        """
        return {
            "title": crm_activity.get("subject", "Attività CRM"),
            "description": crm_activity.get("description") or crm_activity.get("title", ""),
            "start_date": crm_activity.get("activityDate"),
            "end_date": crm_activity.get("activityEndDate"),
            "status": self._map_crm_status(crm_activity.get("status")),
            "priority": self._map_crm_priority(crm_activity.get("priority")),
            "owner_id": str(crm_activity.get("ownerId", "")),
            "owner_name": crm_activity.get("ownerName", ""),
            "customer_id": str(crm_activity.get("companyId", "")),
            "customer_name": crm_activity.get("companyName", ""),
            "account_name": crm_activity.get("accountName", ""),
            "activity_type": crm_activity.get("type", ""),
            "creation_date": crm_activity.get("creationDate"),
            "last_modified_date": crm_activity.get("lastModifiedDate"),
            "crm_activity_id": crm_activity.get("id"),
            "last_synced": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow()
        }
    
    def _map_crm_status(self, crm_status) -> str:
        """Mappa lo status CRM ai valori locali"""
        status_mapping = {
            "aperta": "attiva",
            "chiusa": "completata",
            "in_corso": "in_lavorazione"
        }
        return status_mapping.get(str(crm_status).lower(), "attiva")
    
    def _map_crm_priority(self, crm_priority) -> str:
        """Mappa la priorità CRM ai valori locali"""
        if crm_priority in [0, 1]:
            return "bassa"
        elif crm_priority in [2, 3]:
            return "media"
        else:
            return "alta"
    
    def insert_activity_to_db(self, activity_data: Dict) -> Optional[int]:
        """
        Inserisce un'attività nella tabella activities locale
        
        Args:
            activity_data: Dati attività già mappati
            
        Returns:
            ID dell'attività inserita o None se errore
        """
        try:
            # Query di insert nella tabella activities
            insert_query = text("""
                INSERT INTO activities (
                    title, description, start_date, end_date, status, priority,
                    owner_id, owner_name, customer_id, customer_name, account_name,
                    activity_type, creation_date, last_modified_date, 
                    crm_activity_id, last_synced, created_at
                ) VALUES (
                    :title, :description, :start_date, :end_date, :status, :priority,
                    :owner_id, :owner_name, :customer_id, :customer_name, :account_name,
                    :activity_type, :creation_date, :last_modified_date,
                    :crm_activity_id, :last_synced, :created_at
                ) RETURNING id
            """)
            
            result = self.db.execute(insert_query, activity_data)
            activity_id = result.fetchone()[0]
            
            logger.info(f"✅ Attività inserita: ID={activity_id}, Titolo='{activity_data['title']}'")
            return activity_id
            
        except Exception as e:
            logger.error(f"❌ Errore inserimento attività: {e}")
            return None
    
    def activity_exists(self, crm_activity_id: int) -> bool:
        """Verifica se un'attività CRM è già presente nel DB locale"""
        query = text("SELECT id FROM activities WHERE crm_activity_id = :crm_id")
        result = self.db.execute(query, {"crm_id": crm_activity_id}).fetchone()
        return result is not None
    
    def sync_activities(self, limit: int = 50) -> Dict:
        """
        Processo principale di sincronizzazione
        
        Args:
            limit: Numero massimo di attività da processare
            
        Returns:
            Statistiche dell'operazione di sync
        """
        stats = {
            "start_time": datetime.utcnow().isoformat(),
            "activities_fetched": 0,
            "activities_inserted": 0,
            "activities_skipped": 0,
            "errors": 0
        }
        
        try:
            # 1. Ottieni token CRM
            self.get_crm_token()
            
            # 2. Scarica attività CRM (con filtro client-side)
            crm_activities = self.fetch_activities_by_subtype(limit)
            stats["activities_fetched"] = len(crm_activities)
            
            if not crm_activities:
                logger.warning("⚠️ Nessuna attività CRM con SubType 63705 trovata")
                return stats
            
            # 3. Processa ogni attività
            for crm_activity in crm_activities:
                try:
                    crm_id = crm_activity.get("id")
                    if not crm_id:
                        stats["errors"] += 1
                        continue
                    
                    # Verifica double-check del SubType
                    if crm_activity.get("subTypeId") != INTELLIGENCE_SUBTYPE_ID:
                        logger.warning(f"⚠️ Attività {crm_id} ha SubType {crm_activity.get('subTypeId')}, non {INTELLIGENCE_SUBTYPE_ID} - SALTATA")
                        continue
                    
                    # Controlla se esiste già
                    if self.activity_exists(crm_id):
                        logger.info(f"⏭️ Attività CRM {crm_id} già presente, skip")
                        stats["activities_skipped"] += 1
                        continue
                    
                    # Mappa e inserisci
                    activity_data = self.map_crm_to_local_activity(crm_activity)
                    activity_id = self.insert_activity_to_db(activity_data)
                    
                    if activity_id:
                        stats["activities_inserted"] += 1
                    else:
                        stats["errors"] += 1
                        
                except Exception as e:
                    logger.error(f"❌ Errore processando attività {crm_activity.get('id')}: {e}")
                    stats["errors"] += 1
            
            # 4. Commit delle modifiche
            self.db.commit()
            
            stats["end_time"] = datetime.utcnow().isoformat()
            logger.info(f"🎉 Sync completato: {stats}")
            
        except Exception as e:
            logger.error(f"❌ Errore critico durante sync: {e}")
            self.db.rollback()
            stats["errors"] += 1
            stats["end_time"] = datetime.utcnow().isoformat()
        
        return stats


# Funzione di utilità per uso standalone
def run_sync(limit: int = 50):
    """
    Esegui sync delle attività CRM (funzione standalone)
    
    Args:
        limit: Numero massimo di attività da processare
    """
    # Importa SessionLocal dal path corretto
    try:
        from app.core.database import SessionLocal
    except ImportError:
        # Fallback per esecuzione diretta
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        DATABASE_URL = "postgresql://intelligence_user:intelligence_pass@localhost/intelligence"
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    
    try:
        sync_service = CRMActivitiesSync(db)
        stats = sync_service.sync_activities(limit)
        print(f"📊 Risultati sync: {stats}")
        return stats
    finally:
        db.close()


if __name__ == "__main__":
    # Esecuzione diretta del modulo
    import sys
    
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    print(f"🚀 Avvio sync attività CRM (SubType: {INTELLIGENCE_SUBTYPE_ID}, limit: {limit})")
    
    run_sync(limit)
