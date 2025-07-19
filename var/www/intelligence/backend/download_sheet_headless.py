import os
from dotenv import load_dotenv

import os
import requests
import json
from google.auth.transport.requests import Request
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

# Credenziali
SPREADSHEET_ID = "1Mw0Dtfw9l8CiNQd173gNiyqjZcQcPNLn"
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def get_auth_url():
    """Genera URL per autorizzazione manuale"""
    client_config = {
        "installed": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"]
        }
    }
    
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri="urn:ietf:wg:oauth:2.0:oob"
    )
    
    auth_url, _ = flow.authorization_url(prompt='consent')
    return flow, auth_url

def get_credentials_from_code(flow, auth_code):
    """Ottieni credenziali dal codice di autorizzazione"""
    flow.fetch_token(code=auth_code)
    return flow.credentials

def download_sheet_with_creds(creds):
    """Scarica il sheet con le credenziali"""
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=xlsx"
    headers = {'Authorization': f'Bearer {creds.token}'}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        with open("EndUser_OpportunitaMonitorVendite.xlsx", "wb") as f:
            f.write(response.content)
        print("✅ File scaricato con successo!")
        return True
    else:
        print(f"❌ Errore download: {response.status_code}")
        return False

def main():
    # Controlla se abbiamo già un token
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            if creds.valid:
                return download_sheet_with_creds(creds)
            elif creds.expired and creds.refresh_token:
                creds.refresh(Request())
                return download_sheet_with_creds(creds)
        except:
            pass
    
    # Nuova autorizzazione
    flow, auth_url = get_auth_url()
    
    print("🔗 Vai a questo URL nel browser:")
    print(auth_url)
    print("\n📋 Dopo l'autorizzazione, copia il codice qui:")
    
    auth_code = input("Inserisci il codice di autorizzazione: ").strip()
    
    try:
        creds = get_credentials_from_code(flow, auth_code)
        
        # Salva token per uso futuro
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        
        return download_sheet_with_creds(creds)
        
    except Exception as e:
        print(f"❌ Errore: {str(e)}")
        return False

if __name__ == "__main__":
    main()
