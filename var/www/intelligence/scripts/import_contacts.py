import csv
import psycopg2
from datetime import datetime
import uuid

CSV_FILE = 'data/input/export_contatto_2025-07-0310-35-50.csv'

conn = psycopg2.connect(
    dbname='intelligence',
    user='intelligence_user',
    password='intelligence_pass',
    host='localhost',
    port='5432'
)

cur = conn.cursor()

def parse_date(value):
    try:
        return datetime.strptime(value.strip(), '%d/%m/%Y').date()
    except:
        return None

def parse_int(value):
    try:
        return int(value)
    except:
        return None

def parse_uuid():
    return str(uuid.uuid4())

with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        try:
            contact_id = parse_uuid()
            nome = row['Nome'].strip()
            cognome = row['Cognome'].strip()
            email = row['E-mail'].strip()
            telefono = row['Telefono 1'].strip()
            cellulare = row['Cellulare 1'].strip()
            codice_fiscale = row['Codice fiscale'].strip()
            sesso = parse_int(row['Sesso'])
            ruolo = row['Ruolo aziendale'].strip()
            azienda_nome = row['Azienda'].strip()
            note = row['Note'].strip()
            sales = [s.strip() for s in row['Commerciale di riferimento'].split(',') if s.strip()]
            luogo_nascita = row['Nato a'].strip()
            data_nascita = parse_date(row['Data di nascita'])
            sorgente = row['Origine (Lead)'].strip()
            skype = row['Skype'].strip()
            creato_il = parse_date(row.get('Data creazione ', ''))

            # Trova l'ID dell'azienda
            azienda_id = None
            if azienda_nome:
                cur.execute("SELECT id FROM companies WHERE name ILIKE %s", (azienda_nome,))
                result = cur.fetchone()
                if result:
                    azienda_id = result[0]

            cur.execute("""
                INSERT INTO contacts (
                    id, nome, cognome, email, telefono, sesso, ruolo_aziendale,
                    codice_fiscale, company_id, note, sales_persons,
                    luogo_nascita, data_nascita, sorgente, skype, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s,
                          %s, %s, %s, %s,
                          %s, %s, %s, %s, %s)
            """, (
                contact_id, nome, cognome, email, telefono, sesso, ruolo,
                codice_fiscale, azienda_id, note, sales,
                luogo_nascita, data_nascita, sorgente, skype, creato_il
            ))

        except Exception as e:
            print(f"Errore su riga {row.get('ID')}: {e}")
            conn.rollback()
        else:
            conn.commit()

cur.close()
conn.close()
