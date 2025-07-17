-- Creazione tabella business_cards
-- IntelligenceHUB Business Cards Module

CREATE TABLE IF NOT EXISTS business_cards (
   id VARCHAR PRIMARY KEY,
   filename VARCHAR(255) NOT NULL,
   original_filename VARCHAR(255),
   
   -- Dati estratti
   extracted_data JSONB,
   confidence_score DECIMAL(3,2) DEFAULT 0.0,
   
   -- Campi parsed
   nome VARCHAR(255),
   cognome VARCHAR(255),
   azienda VARCHAR(255),
   posizione VARCHAR(255),
   email VARCHAR(255),
   telefono VARCHAR(100),
   indirizzo TEXT,
   
   -- Stato processing
   status VARCHAR(50) DEFAULT 'uploaded',
   processing_error TEXT,
   
   -- Metadata
   created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
   updated_at TIMESTAMP WITH TIME ZONE,
   processed_at TIMESTAMP WITH TIME ZONE,
   
   -- Relazioni
   company_id INTEGER,
   contact_id INTEGER
);

-- Indici per performance
CREATE INDEX IF NOT EXISTS idx_business_cards_status ON business_cards(status);
CREATE INDEX IF NOT EXISTS idx_business_cards_created_at ON business_cards(created_at);
CREATE INDEX IF NOT EXISTS idx_business_cards_azienda ON business_cards(azienda);
CREATE INDEX IF NOT EXISTS idx_business_cards_confidence ON business_cards(confidence_score);

-- Aggiungi business_card_id a contacts se non esiste
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS business_card_id VARCHAR;
CREATE INDEX IF NOT EXISTS idx_contacts_business_card_id ON contacts(business_card_id);
