#!/bin/bash
echo "🚀 Avvio Backend IntelligenceHUB (PORTA 8000 - CORRETTA)"

# Kill eventuali processi esistenti su porta 8000
echo "🔫 Liberazione porta 8000..."
PORT_PID=$(lsof -ti:8000 2>/dev/null)
if [ ! -z "$PORT_PID" ]; then
    kill -9 $PORT_PID 2>/dev/null
    sleep 2
fi

# Attiva virtual environment
source venv/bin/activate

# Avvia su porta 8000 (ORIGINALE CORRETTA)
echo "🎯 Avvio su porta 8000 (proxy-compatible)..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
