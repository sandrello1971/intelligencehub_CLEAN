#!/bin/bash
echo "🚀 Avvio Backend IntelligenceHUB (TUTTI ENDPOINT)"

# Kill processi esistenti
pkill -f "uvicorn.*8000" 2>/dev/null
sleep 2

# Attiva virtual environment
source venv/bin/activate

# Avvia backend
echo "🎯 Avvio su porta 8000 con endpoint completi..."
echo "📋 Endpoint disponibili:"
echo "   - http://localhost:8000/"
echo "   - http://localhost:8000/health"
echo "   - http://localhost:8000/api/health"
echo "   - http://localhost:8000/api/v1/health"
echo "   - http://localhost:8000/docs"
echo ""

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
