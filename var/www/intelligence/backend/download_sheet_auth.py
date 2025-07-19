import os
from dotenv import load_dotenv

load_dotenv()
import os
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import io

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

# Credenziali dal .env
SPREADSHEET_ID = "1Mw0Dtfw9l8CiNQd173gNiyqjZcQcPNLn"

def authenticate_google():
    """Autentica con Google usando OAuth2"""
    creds = None
    
    # File per salvare i token
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Se non ci sono credenziali valide, chiedi autorizzazione
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Crea credentials dict
            client_config = {
                "installed": {
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
                }
            }
            
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Salva le credenziali per la prossima volta
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

def download_sheet():
    """Scarica il Google Sheet come Excel"""
    try:
        creds = authenticate_google()
        
        # URL per export Excel
        url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=xlsx"
        
        # Headers con autorizzazione
        headers = {'Authorization': f'Bearer {creds.token}'}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            with open("EndUser_OpportunitaMonitorVendite.xlsx", "wb") as f:
                f.write(response.content)
            print("✅ File scaricato con successo!")
            return True
        else:
            print(f"❌ Errore download: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Errore autenticazione: {str(e)}")
        return False

if __name__ == "__main__":
    download_sheet()
