#!/bin/bash
echo "🔄 Executing database schema evolution..."

# Impostazioni database
export PGPASSWORD=intelligence_pass

# Verifica connessione database
echo "1. Testing database connection..."
if ! psql -U intelligence_user -h localhost -d intelligence -c '\dt' > /dev/null 2>&1; then
    echo "❌ Database connection failed"
    echo "Please check your database credentials and connection"
    exit 1
fi
echo "✅ Database connection OK"

# Backup prima dell'evoluzione
echo "2. Creating pre-evolution backup..."
BACKUP_FILE="/var/www/intelligence/data/backups/pre_evolution_$(date +%Y%m%d_%H%M%S).sql"
pg_dump -U intelligence_user -h localhost -d intelligence > "$BACKUP_FILE"
if [ $? -eq 0 ]; then
    echo "✅ Backup created: $BACKUP_FILE"
else
    echo "❌ Backup failed"
    exit 1
fi

# Esegui evoluzione schema
echo "3. Executing schema evolution..."
if psql -U intelligence_user -h localhost -d intelligence -f /var/www/intelligence/backend/scripts/evolution_schema.sql; then
    echo "✅ Schema evolution completed successfully"
else
    echo "❌ Schema evolution failed"
    echo "You can restore from backup: $BACKUP_FILE"
    exit 1
fi

# Verifica risultati
echo "4. Verifying new tables..."
TABLE_COUNT=$(psql -U intelligence_user -h localhost -d intelligence -t -c "
SELECT COUNT(*) FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('knowledge_documents', 'document_chunks', 'ai_conversations', 'bi_cache', 'processing_queue', 'system_health');
")

if [ "$TABLE_COUNT" -eq 6 ]; then
    echo "✅ All 6 new tables created successfully"
else
    echo "❌ Expected 6 tables, found $TABLE_COUNT"
    exit 1
fi

echo "🎉 Database schema evolution completed!"
