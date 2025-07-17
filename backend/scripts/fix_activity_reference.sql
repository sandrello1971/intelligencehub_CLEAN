-- Fix activity_id reference type
-- ==============================================

-- Rimuovi la colonna con tipo sbagliato
ALTER TABLE tickets DROP COLUMN IF EXISTS activity_id;

-- Aggiungi la colonna con tipo corretto (INTEGER)
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS activity_id INTEGER REFERENCES activities(id);

-- Crea indice per performance
CREATE INDEX IF NOT EXISTS idx_tickets_activity ON tickets(activity_id);

\echo '✅ Activity reference fixed!'
