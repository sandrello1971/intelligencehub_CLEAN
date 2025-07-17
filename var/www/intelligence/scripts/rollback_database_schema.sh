#!/bin/bash
echo "🔄 Rolling back database schema changes..."

# Connessione al database
psql -U intelligence_user -d intelligence << 'PSQL_EOF'
-- Rimuovi tabelle in ordine inverso (per foreign keys)
DROP TABLE IF EXISTS system_health CASCADE;
DROP TABLE IF EXISTS processing_queue CASCADE;
DROP TABLE IF EXISTS bi_cache CASCADE;
DROP TABLE IF EXISTS ai_conversations CASCADE;
DROP TABLE IF EXISTS document_chunks CASCADE;
DROP TABLE IF EXISTS knowledge_documents CASCADE;

-- Rimuovi funzione trigger
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;

\echo '✅ Database schema rollback completed'
PSQL_EOF

echo "✅ Database rollback completed"
