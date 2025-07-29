#!/usr/bin/env python3
"""
UPDATE COMPANIES FROM EXCEL - Arricchisce dati esistenti
"""

import os
import logging
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("update_companies_excel")

DATABASE_URL = "postgresql://intelligence_user:intelligence_pass@localhost/intelligence"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def clean_phone(phone):
    if pd.isna(phone) or str(phone).strip() == "":
        return None
    return str(phone).strip()[:20]

def clean_email(email):
    if pd.isna(email) or str(email).strip() == "" or '@' not in str(email):
        return None
    return str(email).strip()[:255]

def update_companies_from_excel(excel_path):
    """Aggiorna aziende esistenti con dati da Excel"""
    
    logger.info(f"📊 Caricamento Excel: {excel_path}")
    
    # Leggi Excel
    df = pd.read_excel(excel_path)
    logger.info(f"📄 Righe Excel: {len(df)}")
    
    stats = {"checked": 0, "updated": 0, "not_found": 0, "errors": 0}
    db = SessionLocal()
    
    try:
        for idx, row in df.iterrows():
            try:
                stats["checked"] += 1
                
                # Dati da Excel
                company_id = int(row['ID'])
                
                # Verifica se esiste nel DB
                existing = db.execute(text("SELECT name FROM companies WHERE id = :id"), 
                                    {"id": company_id}).first()
                
                if not existing:
                    stats["not_found"] += 1
                    continue
                
                # Prepara dati aggiornamento (solo campi non nulli/vuoti)
                update_data = {"id": company_id}
                
                # Telefono
                if not pd.isna(row.get('Telefono')) and str(row.get('Telefono')).strip():
                    update_data["telefono"] = clean_phone(row['Telefono'])
                
                # Email
                if clean_email(row.get('E-mail (azienda)')):
                    update_data["email"] = clean_email(row['E-mail (azienda)'])
                
                # Settore
                if not pd.isna(row.get('Settore merceologico azienda')) and str(row.get('Settore merceologico azienda')).strip():
                    update_data["settore"] = str(row['Settore merceologico azienda']).strip()[:100]
                
                # Sito web
                if not pd.isna(row.get('Sito web')) and str(row.get('Sito web')).strip():
                    update_data["sito_web"] = str(row['Sito web']).strip()[:255]
                
                # Dipendenti
                if not pd.isna(row.get('N° dipendenti')) and row.get('N° dipendenti') > 0:
                    update_data["numero_dipendenti"] = int(row['N° dipendenti'])
                
                # Solo se abbiamo dati da aggiornare
                if len(update_data) > 1:  # > 1 perché abbiamo sempre ID
                    
                    # Build dynamic UPDATE
                    set_clauses = []
                    for key in update_data.keys():
                        if key != "id":
                            set_clauses.append(f"{key} = :{key}")
                    
                    if set_clauses:
                        update_sql = f"UPDATE companies SET {', '.join(set_clauses)} WHERE id = :id"
                        
                        db.execute(text(update_sql), update_data)
                        stats["updated"] += 1
                        
                        logger.info(f"🔄 Aggiornata: {existing[0]} (campi: {len(set_clauses)})")
                
                # Commit ogni 100
                if stats["checked"] % 100 == 0:
                    db.commit()
                    logger.info(f"💾 Progress: {stats['checked']} verificate, {stats['updated']} aggiornate")
                
            except Exception as e:
                logger.error(f"❌ Errore riga {idx}: {e}")
                stats["errors"] += 1
        
        db.commit()
        logger.info(f"✅ Aggiornamento completato: {stats}")
        return stats
        
    except Exception as e:
        db.rollback()
        logger.error(f"💥 Errore fatale: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    excel_path = "/tmp/csv_imports/exportazienda.xlsx"
    
    if not os.path.exists(excel_path):
        logger.error(f"❌ File Excel non trovato: {excel_path}")
        exit(1)
    
    results = update_companies_from_excel(excel_path)
    
    print("\n" + "="*50)
    print("📊 RISULTATI AGGIORNAMENTO AZIENDE")
    print("="*50)
    for key, value in results.items():
        print(f"{key}: {value}")
