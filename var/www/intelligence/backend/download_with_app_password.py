import requests
import base64

# Usa la tua App Password
EMAIL = "s.andrello@enduser-italia.com"
APP_PASSWORD = "tdpa cjac inxl uqxh"
SPREADSHEET_ID = "1Mw0Dtfw9l8CiNQd173gNiyqjZcQcPNLn"

def download_sheet():
    """Scarica sheet con App Password"""
    
    # Metodo 1: Download diretto con autenticazione Basic
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=xlsx&gid=0"
    
    # Codifica credenziali per Basic Auth
    credentials = f"{EMAIL}:{APP_PASSWORD}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'User-Agent': 'Mozilla/5.0 (compatible; Intelligence-Downloader/1.0)'
    }
    
    try:
        print("📡 Tentativo download con App Password...")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            with open("EndUser_OpportunitaMonitorVendite.xlsx", "wb") as f:
                f.write(response.content)
            print("✅ File scaricato con successo!")
            return True
        else:
            print(f"❌ Errore {response.status_code}: {response.text}")
            
        # Metodo 2: Prova URL pubblico semplificato
        print("📡 Tentativo con URL pubblico...")
        public_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=xlsx"
        
        response = requests.get(public_url)
        if response.status_code == 200:
            with open("EndUser_OpportunitaMonitorVendite.xlsx", "wb") as f:
                f.write(response.content)
            print("✅ File scaricato (metodo pubblico)!")
            return True
        else:
            print(f"❌ Anche metodo pubblico fallito: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Errore generale: {str(e)}")
        return False

if __name__ == "__main__":
    success = download_sheet()
    if success:
        print("🎉 Pronto per l'import!")
    else:
        print("💡 Considera upload manuale del file")
