#!/bin/bash
echo "🚀 Avvio Backend IntelligenceHUB (VERSIONE SEMPLIFICATA)"

# Kill eventuali processi esistenti
pkill -f "uvicorn.*8000" 2>/dev/null
sleep 2

# Attiva virtual environment
source venv/bin/activate

# Verifica dipendenze
echo "📦 Verifica dipendenze..."
pip install pydantic-settings >/dev/null 2>&1

# Avvia backend
echo "🎯 Avvio su porta 8000..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
