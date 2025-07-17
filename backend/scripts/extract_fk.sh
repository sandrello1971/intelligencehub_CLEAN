#!/bin/bash
# Script per estrazione Foreign Keys dal database Intelligence
# Crea file CSV con tutte le FK attive

set -e
export PGPASSWORD="intelligence_pass"

OUTPUT_FILE="/var/www/intelligence/backend/fk_map.csv"

psql -U intelligence_user -h localhost -d intelligence -t -A -F ',' -c "
SELECT 
    tc.table_name AS from_table,
    kcu.column_name AS from_column,
    ccu.table_name AS to_table,
    ccu.column_name AS to_column
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu 
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage ccu 
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
ORDER BY tc.table_name, kcu.column_name;
" > \"\$OUTPUT_FILE\"

echo \"✅ FK estratte in: \$OUTPUT_FILE\"
