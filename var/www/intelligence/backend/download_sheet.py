import requests
import os

# Usa le credenziali dal .env se disponibili
sheet_id = "1Mw0Dtfw9l8CiNQd173gNiyqjZcQcPNLn"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"

response = requests.get(url)
if response.status_code == 200:
    with open("EndUser_OpportunitaMonitorVendite.xlsx", "wb") as f:
        f.write(response.content)
    print("✅ File scaricato!")
else:
    print(f"❌ Errore: {response.status_code}")
