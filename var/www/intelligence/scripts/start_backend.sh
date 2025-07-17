#!/bin/bash
# Script avvio backend IntelligenceHUB

echo "🚀 Avvio Backend IntelligenceHUB"
cd /var/www/intelligence/backend

# Attiva virtual environment se esiste
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment attivato"
fi

# Installa dipendenze
pip install -r requirements.txt

# Avvia FastAPI
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
