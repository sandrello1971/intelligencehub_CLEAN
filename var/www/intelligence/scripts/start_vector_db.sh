#!/bin/bash
echo "🚀 Starting Vector Database (Qdrant)..."

cd /var/www/intelligence/docker

# Verifica se Docker è installato
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

# Verifica se Docker Compose è installato
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose first."
    exit 1
fi

# Avvia Qdrant
echo "🔄 Starting Qdrant container..."
docker-compose -f vector-compose.yml up -d qdrant

# Aspetta che il servizio sia pronto
echo "⏳ Waiting for Qdrant to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:6333/health > /dev/null 2>&1; then
        echo "✅ Qdrant is healthy and ready!"
        break
    fi
    
    if [ $i -eq 30 ]; then
        echo "❌ Qdrant failed to start within 30 seconds"
        docker-compose -f vector-compose.yml logs qdrant
        exit 1
    fi
    
    echo "⏳ Waiting... ($i/30)"
    sleep 1
done

# Verifica status
echo "📊 Qdrant Status:"
curl -s http://localhost:6333/health 2>/dev/null || echo "Health check API not responding"

echo "✅ Vector Database setup completed!"
