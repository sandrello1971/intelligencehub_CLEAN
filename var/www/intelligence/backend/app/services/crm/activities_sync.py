#!/usr/bin/env python3
"""
CRM Activities Sync - Intelligence Platform v5.0
Sincronizza attività CRM Intelligence e genera ticket commerciali
"""

import os
import time
import logging
import requests
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

# Import dai modelli esistenti
from backend.app.core.database import SessionLocal

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crm_sync")

# CRM Config
CRM_API_KEY = "r5l50i5lvd.YjuIXg0PPJnqzeldzCBlEpMlwqJPRPFgJppSkPu"
CRM_USERNAME = "intellivoice@enduser-digital.com" 
CRM_PASSWORD = "B4b4in4_07"
CRM_BASE_URL = os.getenv("CRM_BASE_URL", "https://api.crmincloud.it")

# Rate limiting (45 chiamate al minuto)
MAX_CALLS_PER_MINUTE = 45
CALL_INTERVAL = 60 / MAX_CALLS_PER_MINUTE

# SubType ID per attività Intelligence
INTELLIGENCE_SUBTYPE_ID = 63705

class CRMSyncService:
    """Sincronizzatore attività CRM Intelligence"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.token = None
        self.headers = None
        self.kit_names = []
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()
        
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
        
        logger.info("🔐 Getting CRM token...")
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        self.token = response.json()["access_token"]
        self.headers = {
            "Authorization": f"Bearer {self.token}", 
            "WebApiKey": CRM_API_KEY,
            "Content-Type": "application/json"
        }
        
        return self.token
    
    def rate_limited_request(self, url: str) -> requests.Response:
        """Esegui richiesta GET con rate limiting"""
        time.sleep(CALL_INTERVAL)
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response
    
    def load_kit_names(self) -> List[str]:
        """Carica dinamicamente i nomi dei kit commerciali dal DB"""
        logger.info("📦 Loading kit commerciali names...")
        
        query = text("SELECT nome FROM kit_commerciali WHERE attivo = true ORDER BY nome")
        result = self.db.execute(query).fetchall()
        
        self.kit_names = [row.nome for row in result]
        logger.info(f"📦 Loaded {len(self.kit_names)} kit names: {self.kit_names}")
        
        return self.kit_names
    
    def get_activities_ids(self, limit: int = 100) -> List[int]:
        """
        Step 1: Ottieni lista ID delle attività (paginazione 100)
        """
        logger.info(f"📋 Fetching activities IDs (limit={limit})...")
        
        url = f"{CRM_BASE_URL}/api/v1/Activities?limit={limit}"
        response = self.rate_limited_request(url)
        activity_ids = response.json()
        
        logger.info(f"📊 Found {len(activity_ids)} activities")
        return activity_ids
    
    def get_activity_detail(self, activity_id: int) -> Dict:
        """
        Step 2: Ottieni dettaglio singola attività
        """
        url = f"{CRM_BASE_URL}/api/v1/Activities/{activity_id}"
        response = self.rate_limited_request(url)
        return response.json()
    
    def is_intelligence_activity(self, activity: Dict) -> bool:
        """
        Verifica se l'attività è di tipo Intelligence (subTypeId: 63705)
        """
        return activity.get("subTypeId") == INTELLIGENCE_SUBTYPE_ID
    
    def find_kit_in_description(self, description: str) -> Optional[str]:
        """
        Cerca nomi di kit commerciali nella descrizione
        
        Args:
            description: Descrizione dell'attività
            
        Returns:
            Nome del kit trovato o None
        """
        if not description:
            return None
            
        description_upper = description.upper()
        
        for kit_name in self.kit_names:
            # Cerca il nome del kit (case insensitive)
            if kit_name.upper() in description_upper:
                logger.info(f"🎯 Found kit '{kit_name}' in description")
                return kit_name
                
        # Cerca anche versioni parziali (es: "Start Office" se description contiene "start office")
        for kit_name in self.kit_names:
            # Dividi il nome del kit in parole e cerca corrispondenze parziali
            kit_words = kit_name.upper().split()
            if len(kit_words) >= 2:
                # Cerca almeno 2 parole consecutive del kit name
                for i in range(len(kit_words) - 1):
                    partial = " ".join(kit_words[i:i+2])
                    if partial in description_upper:
                        logger.info(f"🎯 Found partial kit match '{kit_name}' via '{partial}'")
                        return kit_name
        
        return None
    
    def find_company_by_crm_id(self, crm_company_id: int) -> Optional[int]:
        """
        Trova company_id nel nostro DB tramite CRM ID
        """
        query = text("SELECT id FROM companies WHERE crm_id = :crm_id")
        result = self.db.execute(query, {"crm_id": str(crm_company_id)}).fetchone()
        return result.id if result else None
    
    def activity_already_processed(self, crm_activity_id: int) -> bool:
        """
        Verifica se l'attività è già stata processata
        """
        query = text("SELECT id FROM tickets WHERE crm_activity_id = :crm_activity_id")
        result = self.db.execute(query, {"crm_activity_id": str(crm_activity_id)}).fetchone()
        return result is not None
    
    def create_commercial_ticket(self, activity: Dict, kit_name: str) -> Optional[int]:
        """
        Crea ticket commerciale padre dall'attività CRM
        
        Args:
            activity: Dati dell'attività CRM
            kit_name: Nome del kit trovato
            
        Returns:
            ID del ticket creato o None se errore
        """
        try:
            # Verifica se già processata
            if self.activity_already_processed(activity["id"]):
                logger.info(f"⏭️ Activity {activity['id']} already processed, skipping")
                return None
            
            # Trova azienda collegata
            company_id = None
            if activity.get("companyId"):
                company_id = self.find_company_by_crm_id(activity["companyId"])
                if not company_id:
                    logger.warning(f"⚠️ Company not found for CRM ID: {activity['companyId']}")
            
            # Genera subject del ticket
            subject = f"Richiesta Commerciale - {kit_name}"
            if activity.get("subject"):
                subject = f"{activity['subject']} - {kit_name}"
            
            # Prepara descrizione arricchita
            description = f"Ticket generato automaticamente da attività CRM Intelligence.\n\n"
            description += f"Kit Commerciale Richiesto: {kit_name}\n"
            description += f"Attività CRM ID: {activity['id']}\n"
            if activity.get("description"):
                description += f"\nDescrizione originale:\n{activity['description']}"
            
            # Inserisci ticket nel database
            insert_query = text("""
                INSERT INTO tickets (
                    subject, description, tipo, priority, status, 
                    company_id, crm_activity_id, created_by, created_at
                ) VALUES (
                    :subject, :description, :tipo, :priority, :status,
                    :company_id, :crm_activity_id, :created_by, :created_at
                ) RETURNING id
            """)
            
            result = self.db.execute(insert_query, {
                "subject": subject,
                "description": description,
                "tipo": "commerciale",
                "priority": "media",
                "status": "aperto", 
                "company_id": company_id,
                "crm_activity_id": str(activity["id"]),
                "created_by": "CRM_SYNC",
                "created_at": datetime.utcnow()
            }).fetchone()
            
            self.db.commit()
            
            ticket_id = result.id
            logger.info(f"✅ Created ticket {ticket_id} for kit '{kit_name}' from activity {activity['id']}")
            
            return ticket_id
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error creating ticket for activity {activity['id']}: {e}")
            return None
    
    def sync_activities(self, limit: int = 100) -> Dict[str, int]:
        """
        Processo principale di sincronizzazione
        
        Args:
            limit: Numero massimo di attività da processare
            
        Returns:
            Statistiche della sincronizzazione
        """
        stats = {
            "activities_checked": 0,
            "intelligence_activities": 0,
            "tickets_created": 0,
            "errors": 0
        }
        
        try:
            # Setup iniziale
            self.get_crm_token()
            self.load_kit_names()
            
            if not self.kit_names:
                logger.warning("⚠️ No kit commerciali found, aborting sync")
                return stats
            
            # Step 1: Ottieni lista ID attività
            activity_ids = self.get_activities_ids(limit)
            stats["activities_checked"] = len(activity_ids)
            
            # Step 2: Processa ogni attività
            for activity_id in activity_ids:
                try:
                    # Ottieni dettaglio attività
                    activity = self.get_activity_detail(activity_id)
                    
                    # Verifica se è di tipo Intelligence
                    if not self.is_intelligence_activity(activity):
                        continue
                        
                    stats["intelligence_activities"] += 1
                    logger.info(f"🔍 Processing Intelligence activity {activity_id}")
                    
                    # Cerca kit nella descrizione
                    description = activity.get("description", "")
                    kit_found = self.find_kit_in_description(description)
                    
                    if not kit_found:
                        logger.info(f"📝 No kit found in activity {activity_id} description")
                        continue
                    
                    # Crea ticket commerciale
                    ticket_id = self.create_commercial_ticket(activity, kit_found)
                    if ticket_id:
                        stats["tickets_created"] += 1
                        
                except Exception as e:
                    logger.error(f"❌ Error processing activity {activity_id}: {e}")
                    stats["errors"] += 1
                    continue
            
            # Log finale
            logger.info(f"🏁 Sync completed: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"💥 Fatal error during sync: {e}")
            stats["errors"] += 1
            return stats

def main():
    """Funzione principale per eseguire la sincronizzazione"""
    logger.info("🚀 Starting CRM Activities Sync...")
    
    with CRMSyncService() as sync_service:
        stats = sync_service.sync_activities(limit=100)
        
    logger.info("✨ Sync completed!")
    return stats

if __name__ == "__main__":
    main()
