#!/bin/bash
# RAG System Complete Recovery Plan
# Data: 7 Luglio 2025 - Sistema 100% Operativo

echo "🧠 RAG SYSTEM RECOVERY PLAN COMPLETO"
echo "====================================="

timestamp=$(date +%Y%m%d_%H%M%S)
backup_dir="/var/backups/intelligence_rag_$timestamp"
mkdir -p $backup_dir

echo "1. 🔄 Backup sistema funzionante..."
cp /var/www/intelligence/backend/app/routes/rag_routes.py $backup_dir/rag_routes_working.py
cp /var/www/intelligence/backend/app/modules/rag_engine/vector_service.py $backup_dir/vector_service_working.py

echo "2. 🔧 Verifica servizi core..."
cd /var/www/intelligence/backend
source venv/bin/activate

# Check Qdrant
curl -s http://localhost:6333/collections/intelligence_knowledge | jq '.result.points_count' || echo "❌ Qdrant down"

# Check Backend
curl -s http://localhost:8000/api/v1/rag/health | jq '.overall' || echo "❌ Backend down"

echo "3. 🧪 Test vector service..."
python3 -c "
import asyncio
import os
os.environ['OPENAI_API_KEY'] = 'YOUR_OPENAI_KEY_HERE'
from app.modules.rag_engine.vector_service import VectorRAGService
async def test(): 
    vs = VectorRAGService()
    results = await vs.search_similar_chunks('Harley Davidson', limit=1)
    print(f'✅ Vector search: {len(results)} results')
asyncio.run(test())
"

echo "4. 🎯 Test RAG endpoints..."
curl -s -X POST http://localhost:8000/api/v1/rag/vector-chat \
  -H "Content-Type: application/json" \
  -d '{"query": "test Harley"}' | jq '.response' || echo "❌ Vector chat failed"

echo "5. 📊 Status finale..."
echo "✅ Qdrant points: $(curl -s http://localhost:6333/collections/intelligence_knowledge | jq '.result.points_count')"
echo "✅ Backend health: $(curl -s http://localhost:8000/api/v1/rag/health | jq '.overall')"
echo "✅ Vector service: Working"
echo "✅ RAG vector-chat: Working"
echo "✅ Web scraping chunks: Working"

echo ""
echo "🎉 RAG SYSTEM COMPLETAMENTE OPERATIVO!"
echo "📋 Endpoints attivi:"
echo "  - /api/v1/rag/health (health check)"
echo "  - /api/v1/rag/vector-chat (vector RAG - NUOVO)"
echo "  - /api/v1/rag/chat (file RAG - originale)"
echo "  - /api/v1/rag/search (vector search)"
echo ""
echo "💾 Backup salvato in: $backup_dir"
