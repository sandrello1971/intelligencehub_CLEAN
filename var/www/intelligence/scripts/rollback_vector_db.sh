#!/bin/bash
echo "🔄 Rolling back Vector DB setup..."
docker-compose -f docker/vector-compose.yml down
docker volume rm intelligence_qdrant_data 2>/dev/null || true
rm -rf /var/www/intelligence/data/qdrant
echo "✅ Vector DB rollback completed"
