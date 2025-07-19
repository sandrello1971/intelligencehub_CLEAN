#!/usr/bin/env python3
"""
Sales Opportunities Excel Import Script
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, date
from typing import Optional, Dict, Any
import re
from difflib import SequenceMatcher
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database config
DATABASE_URL = "postgresql://intelligence_user:intelligence_pass@localhost/intelligence"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Sales Manager mapping
SALES_MANAGERS = {
   "PierLuigiMenin": {"email": "p.menin@enduser-italia.com", "type": "account_manager"},
   "GiovanniFulgheri": {"email": "g.fulgheri@enduser-italia.com", "type": "account_manager"},
   "FabrizioCorbinelli": {"email": "f.corbinelli@enduser-italia.com", "type": "account_manager"},
   "FrancescaDeVita": {"email": "f.devita@enduser-italia.com", "type": "account_manager"},
   "FabioAliboni": {"email": "f.aliboni@enduser-italia.com", "type": "area_manager"},
   "MariaSilviaGentile": {"email": "ms.gentile@enduser-italia.com", "type": "area_manager"}
}

class SalesOpportunitiesImporter:
   def __init__(self, excel_file_path: str):
       self.excel_file_path = excel_file_path
       self.db = SessionLocal()
       self.load_user_ids()
       self.stats = {"processed": 0, "imported": 0, "errors": []}
   
   def load_user_ids(self):
       for sheet_name, manager_info in SALES_MANAGERS.items():
           result = self.db.execute(text("SELECT id FROM users WHERE email = :email"), 
                                  {"email": manager_info["email"]}).fetchone()
           if result:
               manager_info["user_id"] = str(result[0])
               print(f"✅ Found user {sheet_name}: {manager_info['user_id']}")
           else:
               print(f"❌ User not found for {sheet_name}")
   
   def clean_string(self, value) -> Optional[str]:
       if pd.isna(value) or value is None:
           return None
       cleaned = str(value).strip()
       return cleaned if cleaned else None
   
   def normalize_date(self, date_value) -> Optional[date]:
       if pd.isna(date_value) or date_value is None:
           return None
       try:
           if isinstance(date_value, str):
               if date_value.strip() == "":
                   return None
               for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"]:
                   try:
                       return datetime.strptime(date_value.strip(), fmt).date()
                   except ValueError:
                       continue
               return None
           elif isinstance(date_value, (datetime, pd.Timestamp)):
               return date_value.date()
           elif isinstance(date_value, date):
               return date_value
           else:
               return None
       except Exception:
           return None
   
   def normalize_decimal(self, value) -> Optional[float]:
       if pd.isna(value) or value is None:
           return None
       try:
           if isinstance(value, str):
               cleaned = re.sub(r'[^\d.,\-]', '', value.strip())
               if not cleaned:
                   return None
               cleaned = cleaned.replace(',', '.')
               return float(cleaned)
           else:
               return float(value)
       except (ValueError, TypeError):
           return None
   
   def parse_boolean(self, value) -> Optional[bool]:
       if pd.isna(value) or value is None:
           return None
       value_str = str(value).lower().strip()
       if value_str in ['sì', 'si', 'yes', 'true', '1']:
           return True
       elif value_str in ['no', 'false', '0']:
           return False
       else:
           return None
   
   def process_sheet(self, sheet_name: str) -> int:
       if sheet_name not in SALES_MANAGERS:
           print(f"⚠️ Sheet '{sheet_name}' non riconosciuto")
           return 0
       
       manager_info = SALES_MANAGERS[sheet_name]
       if not manager_info.get("user_id"):
           print(f"❌ User ID non trovato per {sheet_name}")
           return 0
           
       print(f"\n📋 Processing sheet: {sheet_name}")
       
       try:
           df = pd.read_excel(self.excel_file_path, sheet_name=sheet_name)
           
           if df.empty:
               print(f"⚠️ Sheet '{sheet_name}' è vuoto")
               return 0
           
           print(f"📊 Rows found: {len(df)}")
           
           imported_count = 0
           
           for index, row in df.iterrows():
               try:
                   self.stats["processed"] += 1
                   
                   # Skip header e righe vuote
                   if index == 0 or pd.isna(row.iloc[2]) or str(row.iloc[2]).strip() == "":
                       continue
                   
                   cliente = self.clean_string(row.iloc[2])  # Cliente
                   if not cliente:
                       continue
                   
                   # Dati base
                   data_apertura = self.normalize_date(row.iloc[0])
                   stato_opportunita = self.clean_string(row.iloc[10])
                   valore_opportunita = self.normalize_decimal(row.iloc[12])
                   
                   # Insert base
                   insert_query = text("""
                       INSERT INTO sales_opportunities (
                           sales_manager_id, sales_manager_type, cliente,
                           data_apertura, stato_opportunita, valore_opportunita
                       ) VALUES (
                           :sales_manager_id, :sales_manager_type, :cliente,
                           :data_apertura, :stato_opportunita, :valore_opportunita
                       )
                   """)
                   
                   self.db.execute(insert_query, {
                       "sales_manager_id": manager_info["user_id"],
                       "sales_manager_type": manager_info["type"],
                       "cliente": cliente,
                       "data_apertura": data_apertura,
                       "stato_opportunita": stato_opportunita,
                       "valore_opportunita": valore_opportunita
                   })
                   
                   imported_count += 1
                   self.stats["imported"] += 1
                       
               except Exception as e:
                   error_msg = f"Error row {index}: {str(e)}"
                   print(f"❌ {error_msg}")
                   self.stats["errors"].append(error_msg)
                   continue
           
           self.db.commit()
           print(f"✅ Sheet '{sheet_name}' completed: {imported_count} opportunities")
           return imported_count
           
       except Exception as e:
           self.db.rollback()
           error_msg = f"Error sheet {sheet_name}: {str(e)}"
           print(f"❌ {error_msg}")
           self.stats["errors"].append(error_msg)
           return 0
   
   def run_import(self):
       print("🚀 Starting Import")
       
       try:
           if not os.path.exists(self.excel_file_path):
               raise FileNotFoundError(f"File non trovato: {self.excel_file_path}")
           
           # Pulisci tabella
           response = input("🗑️ Pulire tabella sales_opportunities? (y/N): ")
           if response.lower() == 'y':
               self.db.execute(text("DELETE FROM sales_opportunities"))
               self.db.commit()
               print("✅ Tabella pulita")
           
           # Processa sheets
           total_imported = 0
           for sheet_name in SALES_MANAGERS.keys():
               imported = self.process_sheet(sheet_name)
               total_imported += imported
           
           print(f"\n📊 COMPLETED: {self.stats['imported']} imported, {len(self.stats['errors'])} errors")
           
       except Exception as e:
           print(f"💥 FATAL ERROR: {str(e)}")
           self.db.rollback()
       finally:
           self.db.close()

def main():
   if len(sys.argv) != 2:
       print("Usage: python3 excel_import_script.py <excel_file>")
       sys.exit(1)
   
   importer = SalesOpportunitiesImporter(sys.argv[1])
   importer.run_import()

if __name__ == "__main__":
   main()
