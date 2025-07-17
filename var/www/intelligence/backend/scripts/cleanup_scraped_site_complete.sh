#!/bin/bash
# Script per vedere tutti i dati che devono essere eliminati per un sito

echo "🧹 CLEANUP SCRAPED SITE - ANALISI COMPLETA"
echo "==========================================="

# Analisi tabelle da pulire
echo "📊 Tabelle che contengono dati di scraping:"
PGPASSWORD=intelligence_pass psql -U intelligence_user -h localhost -d intelligence -c "
SELECT table_name, column_name 
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND (column_name LIKE '%url%' OR column_name LIKE '%filename%' OR column_name LIKE '%website%')
AND table_name IN (
    'knowledge_documents', 
    'scraped_websites', 
    'scraped_content', 
    'scraped_contacts', 
    'scraped_companies',
    'document_chunks'
)
ORDER BY table_name, column_name;
"

echo ""
echo "🔍 Dati attuali per sito di esempio:"
PGPASSWORD=intelligence_pass psql -U intelligence_user -h localhost -d intelligence -c "
-- Knowledge documents
SELECT 'knowledge_documents' as table_name, COUNT(*) as count 
FROM knowledge_documents 
WHERE filename LIKE '%scraped_20250707_075007%'

UNION ALL

-- Document chunks 
SELECT 'document_chunks' as table_name, COUNT(*) as count 
FROM document_chunks 
WHERE document_id IN (
    SELECT id FROM knowledge_documents 
    WHERE filename LIKE '%scraped_20250707_075007%'
)

UNION ALL

-- Scraped websites
SELECT 'scraped_websites' as table_name, COUNT(*) as count 
FROM scraped_websites 
WHERE url LIKE '%scraped_20250707_075007%';
"

