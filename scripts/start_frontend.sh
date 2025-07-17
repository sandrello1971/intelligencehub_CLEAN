#!/bin/bash
# Script avvio frontend IntelligenceHUB

echo "🚀 Avvio Frontend IntelligenceHUB"
cd /var/www/intelligence/frontend

# Installa dipendenze
npm install

# Avvia development server
npm run dev
