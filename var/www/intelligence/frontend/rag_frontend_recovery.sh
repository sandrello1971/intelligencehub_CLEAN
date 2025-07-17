#!/bin/bash
echo "🔧 RAG Frontend Recovery Plan"
echo "============================="

# 1. Backup componenti esistenti
echo "1. Creating backups..."
cp -r /var/www/intelligence/frontend/src /var/www/intelligence/frontend/src.backup-$(date +%Y%m%d_%H%M%S)

# 2. Verifica struttura frontend
echo "2. Checking frontend structure..."
ls -la /var/www/intelligence/frontend/src/components/ 2>/dev/null || echo "❌ Components dir missing"
ls -la /var/www/intelligence/frontend/src/pages/ 2>/dev/null || echo "❌ Pages dir missing"

# 3. Verifica API backend
echo "3. Testing backend API..."
curl -s http://localhost:8000/api/v1/rag/health | grep -q "overall.*true" && echo "✅ RAG API: OK" || echo "❌ RAG API: FAILED"

echo "🎯 Recovery plan ready"
