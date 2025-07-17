#!/bin/bash
# Script test sistema IntelligenceHUB - PORTA 8000 CORRETTA

echo "🧪 Test Sistema IntelligenceHUB (PORTA 8000)"
echo "============================================="

# Test database connection
echo "🔍 Test connessione database..."
if PGPASSWORD=intelligence_pass psql -h localhost -U intelligence_user -d intelligence -c "SELECT 1;" >/dev/null 2>&1; then
    echo "✅ Database: OK"
else
    echo "❌ Database: FAIL"
fi

# Test backend API (PORTA 8000 - CORRETTA)
echo "🔍 Test backend API (porta 8000 - PROXY COMPATIBLE)..."
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ Backend API (8000): OK"
    curl -s http://localhost:8000/health | jq '.' 2>/dev/null || curl -s http://localhost:8000/health
else
    echo "❌ Backend API (8000): FAIL"
fi

# Test frontend
echo "🔍 Test frontend (porta 3000)..."
if curl -s http://localhost:3000 >/dev/null 2>&1; then
    echo "✅ Frontend: OK"
else
    echo "❌ Frontend: FAIL"
fi

# Test proxy (3000 → 8000)
echo "🔍 Test proxy (3000/api → 8000)..."
if curl -s http://localhost:3000/api/health >/dev/null 2>&1; then
    echo "✅ Proxy: OK (3000/api → 8000)"
else
    echo "❌ Proxy: FAIL"
fi

echo ""
echo "📊 Status Porte CORRETTE:"
echo "- Porta 8000 (Backend): $(lsof -ti:8000 >/dev/null 2>&1 && echo 'OCCUPATA ✅' || echo 'LIBERA ❌')"
echo "- Porta 3000 (Frontend): $(lsof -ti:3000 >/dev/null 2>&1 && echo 'OCCUPATA ✅' || echo 'LIBERA ❌')"
echo ""
echo "🎯 URLs CORRETTI:"
echo "- Frontend: http://localhost:3000"
echo "- Backend: http://localhost:8000"
echo "- API Docs: http://localhost:8000/docs"
echo "- Admin: http://localhost:3000/admin/tipi-commesse"
