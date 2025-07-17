#!/bin/bash
echo "🚀 Avvio Frontend IntelligenceHUB (PROXY → 8000)"

# Kill eventuali processi esistenti su porta 3000
PORT_PID=$(lsof -ti:3000 2>/dev/null)
if [ ! -z "$PORT_PID" ]; then
    echo "🔫 Terminando processo su porta 3000..."
    kill -9 $PORT_PID 2>/dev/null
    sleep 2
fi

# Verifica dipendenze
if [ ! -d "node_modules" ]; then
    echo "📦 Installazione dipendenze..."
    npm install --legacy-peer-deps
fi

echo "🎯 Proxy configurato: localhost:3000/api → localhost:8000"
npm run dev
