#!/bin/bash
echo "📊 Vector Database Monitoring"
echo "============================"

# Container Status
echo "🐳 Container Status:"
docker ps --filter "name=intelligence_qdrant" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "💾 Storage Usage:"
du -sh /var/www/intelligence/data/qdrant/

echo ""
echo "🔍 Health Status:"
curl -s http://localhost:6333/health 2>/dev/null || echo "Health check failed"

echo ""
echo "📈 Collections Info:"
curl -s http://localhost:6333/collections 2>/dev/null || echo "Collections API failed"

echo ""
echo "🔗 Network Connectivity:"
if nc -z localhost 6333; then
    echo "✅ Port 6333 is accessible"
else
    echo "❌ Port 6333 is not accessible"
fi
