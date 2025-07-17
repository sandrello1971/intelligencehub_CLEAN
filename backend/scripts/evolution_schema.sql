-- ==============================================
-- INTELLIGENCE PLATFORM - DATABASE EVOLUTION
-- Phase 1: RAG Knowledge Management Tables
-- ==============================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==============================================
-- 1. KNOWLEDGE MANAGEMENT TABLES
-- ==============================================

-- Main documents table
CREATE TABLE IF NOT EXISTS knowledge_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename VARCHAR(255) NOT NULL,
    content_type VARCHAR(100),
    file_size BIGINT,
    content_hash VARCHAR(64),
    extracted_text TEXT,
    metadata JSONB DEFAULT '{}',
    processed_at TIMESTAMP,
    company_id INTEGER REFERENCES companies(id),
    uploaded_by UUID, -- Soft reference to users
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Document chunks for Vector DB mapping
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES knowledge_documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content_chunk TEXT NOT NULL,
    vector_id VARCHAR(100), -- ID in Qdrant
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- 2. AI CONVERSATION SYSTEM
-- ==============================================

-- AI conversations history
CREATE TABLE IF NOT EXISTS ai_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID, -- Soft reference to users
    company_id INTEGER REFERENCES companies(id),
    conversation_id VARCHAR(100),
    message_type VARCHAR(20) CHECK (message_type IN ('user', 'assistant', 'system')),
    content TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- 3. BUSINESS INTELLIGENCE & CACHE
-- ==============================================

-- Business intelligence cache
CREATE TABLE IF NOT EXISTS bi_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    data JSONB,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- 4. SYSTEM MANAGEMENT
-- ==============================================

-- Processing queue for async jobs
CREATE TABLE IF NOT EXISTS processing_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_type VARCHAR(100) NOT NULL,
    job_data JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);

-- System health monitoring
CREATE TABLE IF NOT EXISTS system_health (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    details JSONB,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- 5. PERFORMANCE INDICES
-- ==============================================

-- Knowledge documents indices
CREATE INDEX IF NOT EXISTS idx_knowledge_documents_company ON knowledge_documents(company_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_documents_hash ON knowledge_documents(content_hash);
CREATE INDEX IF NOT EXISTS idx_knowledge_documents_processed ON knowledge_documents(processed_at);

-- Document chunks indices
CREATE INDEX IF NOT EXISTS idx_document_chunks_document ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_vector ON document_chunks(vector_id);

-- AI conversations indices
CREATE INDEX IF NOT EXISTS idx_ai_conversations_user ON ai_conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_conversations_company ON ai_conversations(company_id);
CREATE INDEX IF NOT EXISTS idx_ai_conversations_conversation ON ai_conversations(conversation_id);

-- BI cache indices
CREATE INDEX IF NOT EXISTS idx_bi_cache_key ON bi_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_bi_cache_expires ON bi_cache(expires_at);

-- Processing queue indices
CREATE INDEX IF NOT EXISTS idx_processing_queue_status ON processing_queue(status);
CREATE INDEX IF NOT EXISTS idx_processing_queue_type ON processing_queue(job_type);

-- System health indices
CREATE INDEX IF NOT EXISTS idx_system_health_service ON system_health(service_name);
CREATE INDEX IF NOT EXISTS idx_system_health_checked ON system_health(checked_at);

-- ==============================================
-- 6. TRIGGERS AND FUNCTIONS
-- ==============================================

-- Function to update updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for knowledge_documents
DROP TRIGGER IF EXISTS update_knowledge_documents_updated_at ON knowledge_documents;
CREATE TRIGGER update_knowledge_documents_updated_at 
    BEFORE UPDATE ON knowledge_documents 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==============================================
-- 7. TABLE COMMENTS (DOCUMENTATION)
-- ==============================================

COMMENT ON TABLE knowledge_documents IS 'Enterprise knowledge management - document storage and metadata';
COMMENT ON TABLE document_chunks IS 'Document chunks for vector database integration';
COMMENT ON TABLE ai_conversations IS 'AI agent conversation history and context';
COMMENT ON TABLE bi_cache IS 'Business intelligence cache for performance optimization';
COMMENT ON TABLE processing_queue IS 'Asynchronous job processing queue';
COMMENT ON TABLE system_health IS 'System health monitoring and alerting';

-- ==============================================
-- 8. INITIAL DATA
-- ==============================================

-- Insert initial system health record
INSERT INTO system_health (service_name, status, details)
VALUES ('database_evolution', 'completed', '{"version": "1.0", "timestamp": "' || CURRENT_TIMESTAMP || '"}')
ON CONFLICT DO NOTHING;

-- ==============================================
-- 9. VERIFICATION QUERIES
-- ==============================================

-- Verify all tables were created
SELECT 
    schemaname, 
    tablename, 
    tableowner
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN (
    'knowledge_documents', 
    'document_chunks', 
    'ai_conversations', 
    'bi_cache', 
    'processing_queue', 
    'system_health'
);

-- Show table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

\echo '✅ Database schema evolution completed successfully!'
