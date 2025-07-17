import pandas as pd
import psycopg2
import json
from datetime import datetime

DB_PARAMS = {
    'host': 'localhost',
    'port': 5432,
    'dbname': 'intelligence',
    'user': 'intelligence_user',
    'password': 'intelligence_pass'
}

CSV_FILE = 'data/input/export_aziende.csv'

def try_parse_int(value):
    try:
        return int(value)
    except:
        return None

def parse_date(value):
    if pd.isna(value):
        return None
    try:
        return pd.to_datetime(value).date()
    except:
        return None

def parse_csv(path):
    try:
        df = pd.read_csv(path)
    except Exception as e:
        print(f"Errore durante la lettura del file CSV: {e}")
        exit(1)
    return df

def insert_companies(df):
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()

    for _, row in df.iterrows():
        try:
            cur.execute("""
                INSERT INTO companies (
                    id, name, citta, provincia, regione, stato,
                    cap, indirizzo, partita_iva, codice_fiscale,
                    sito_web, note, score, numero_dipendenti, email,
                    telefono, zona_commerciale, sales_persons, data_acquisizione
                )
                VALUES (%s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s)
            """, (
                row['ID'],
                row['Azienda'],
                row['Città (Azienda)'],
                row['Provincia (Azienda)'],
                row['Regione (Azienda)'],
                row['Nazione (Azienda)'] or 'IT',
                str(row['CAP']) if not pd.isna(row['CAP']) else None,
                row['Indirizzo'],
                row['Partita IVA'],
                row['Codice fiscale'],
                row['Sito web'],
                row['Descrizione società'],
                try_parse_int(row['Score']),
                try_parse_int(row['N° dipendenti']),
                row['E-mail (azienda)'],
                row['Telefono'],
                row['Zona'],
                json.dumps([row['Commerciale di riferimento']]) if not pd.isna(row['Commerciale di riferimento']) else json.dumps([]),
                parse_date(row['Cliente da'])
            ))
        except Exception as e:
            print(f"Errore su riga {row['ID']}: {e}")
            conn.rollback()
        else:
            conn.commit()

    cur.close()
    conn.close()

if __name__ == '__main__':
    df = parse_csv(CSV_FILE)
    insert_companies(df)
