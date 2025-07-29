#!/usr/bin/env python3
"""
BULK CONTACTS IMPORT - Skip aziende, solo contatti
"""

import os
import csv
import sys
import logging
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bulk_contacts_import")

DATABASE_URL = "postgresql://intelligence_user:intelligence_pass@localhost/intelligence"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def clean_phone(phone):
    if not phone or str(phone).strip() == "" or str(phone) == "nan":
        return None
    return re.sub(r'[^\d+]', '', str(phone))[:20]

def safe_date(date_str):
    if not date_str or str(date_str) == "nan":
        return None
    try:
        return datetime.strptime(str(date_str), "%d/%m/%Y %H:%M:%S").date()
    except:
        try:
            return datetime.strptime(str(date_str), "%d/%m/%Y").date()
        except:
            return None

def find_company_id_by_name(company_name, db):
    """Trova company_id dal nome azienda"""
    if not company_name or company_name.strip() == "":
        return None
    
    # Cerca per nome esatto
    result = db.execute(text("SELECT id FROM companies WHERE LOWER(name) = LOWER(:name)"), 
                       {"name": company_name.strip()}).first()
    
    if result:
        return result[0]
    
    # Fallback: cerca per LIKE
    result = db.execute(text("SELECT id FROM companies WHERE LOWER(name) LIKE LOWER(:pattern)"), 
                       {"pattern": f"%{company_name.strip()}%"}).first()
    
    if result:
        logger.info(f"📍 Match parziale: '{company_name}' -> ID {result[0]}")
        return result[0]
    
    logger.warning(f"❌ Azienda non trovata: '{company_name}'")
    return None

def process_contact_row(row, db):
    """Processa contatto dal CSV"""
    
    # Trova company_id
    company_id = None
    if row.get("Azienda"):
        company_id = find_company_id_by_name(row["Azienda"], db)
    
    return {
        "company_id": company_id,
        "nome": str(row.get("Nome", "")).strip()[:100] or None,
        "cognome": str(row.get("Cognome", "")).strip()[:100] or None,
        "codice": str(row.get("Codice", "")).strip()[:20] or None,
        "ruolo_aziendale": str(row.get("Ruolo aziendale", "")).strip()[:100] or None,
        "email": str(row.get("E-mail", "")).strip()[:255] or None,
        "telefono": clean_phone(row.get("Telefono 1")),
        "indirizzo": str(row.get("Indirizzo (Primario)", "")).strip()[:255] or None,
        "citta": str(row.get("Città (Primario)", "")).strip()[:100] or None,
        "cap": str(row.get("CAP (Primario)", "")).strip()[:10] or None,
        "provincia": str(row.get("Provincia (Primario)", "")).strip()[:10] or None,
        "regione": str(row.get("Regione (Primario)", "")).strip()[:50] or None,
        "stato": str(row.get("Nazione (Primario)", "")).strip()[:50] or None,
        "codice_fiscale": str(row.get("Codice fiscale", "")).strip()[:20] or None,
        "data_nascita": safe_date(row.get("Data di nascita")),
        "luogo_nascita": str(row.get("Nato a", "")).strip()[:100] or None,
        "sesso": 1 if row.get("Sesso") == "Maschile" else (2 if row.get("Sesso") == "Femminile" else None),
        "skype": str(row.get("Skype", "")).strip()[:100] or None,
        "note": f"Import CRM - ID: {row.get('ID CRM', '')}\nProprietario: {row.get('Proprietario', '')}\nCommerciale: {row.get('Commerciale di riferimento', '')}",
        "sorgente": "CRM_BULK_IMPORT",
        "created_at": safe_date(row.get("Data creazione ")) or datetime.utcnow()
    }

def bulk_import_contacts(csv_path):
    """Import contatti"""
    
    logger.info(f"👥 Avvio import contatti da {csv_path}")
    
    stats = {"total": 0, "created": 0, "with_company": 0, "without_company": 0, "errors": 0}
    db = SessionLocal()
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row_num, row in enumerate(reader, 1):
                try:
                    stats["total"] += 1
                    
                    # Skip se mancano dati essenziali
                    if not row.get("ID") or (not row.get("Nome") and not row.get("Cognome")):
                        continue
                    
                    contact_data = process_contact_row(row, db)
                    
                    # Track statistiche
                    if contact_data["company_id"]:
                        stats["with_company"] += 1
                    else:
                        stats["without_company"] += 1
                    
                    # Insert contatto (sempre nuovo - UUID auto-generato)
                    insert_sql = text("""
                    INSERT INTO contacts (
                        company_id, nome, cognome, codice, ruolo_aziendale, email, telefono,
                        indirizzo, citta, cap, provincia, regione, stato, codice_fiscale,
                        data_nascita, luogo_nascita, sesso, skype, note, sorgente, created_at
                    ) VALUES (
                        :company_id, :nome, :cognome, :codice, :ruolo_aziendale, :email, :telefono,
                        :indirizzo, :citta, :cap, :provincia, :regione, :stato, :codice_fiscale,
                        :data_nascita, :luogo_nascita, :sesso, :skype, :note, :sorgente, :created_at
                    )
                    """)
                    
                    db.execute(insert_sql, contact_data)
                    stats["created"] += 1
                    
                    nome_completo = f"{contact_data['nome'] or ''} {contact_data['cognome'] or ''}".strip()
                    logger.info(f"➕ Contatto {stats['created']}: {nome_completo}")
                    
                    # Commit ogni 100
                    if row_num % 100 == 0:
                        db.commit()
                        logger.info(f"💾 Progress: {row_num} righe, {stats['created']} contatti creati")
                
                except Exception as e:
                    logger.error(f"❌ Errore riga {row_num}: {e}")
                    stats["errors"] += 1
        
        db.commit()
        logger.info(f"✅ Import completato: {stats}")
        return stats
        
    except Exception as e:
        db.rollback()
        logger.error(f"💥 Errore fatale: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    csv_path = "/tmp/csv_imports/exportcontatti.csv"
    results = bulk_import_contacts(csv_path)
    
    print("\n" + "="*50)
    print("📊 RISULTATI IMPORT CONTATTI")
    print("="*50)
    for key, value in results.items():
        print(f"{key}: {value}")
