-- Intelligence Platform v5.0 - Complete Database Schema
-- Domain: intelligencehub.enduser-digital.com
-- ==============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==============================================
-- USERS AND PERMISSIONS
-- ==============================================

-- Enhanced users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS first_name VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_name VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS permissions JSONB DEFAULT '{}';
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;

-- Roles table
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    permissions JSONB DEFAULT '{}',
    is_system_role BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- PROJECT STRUCTURE ENHANCEMENT
-- ==============================================

-- Enhanced commesse table
ALTER TABLE commesse ADD COLUMN IF NOT EXISTS client_id INTEGER REFERENCES companies(id);
ALTER TABLE commesse ADD COLUMN IF NOT EXISTS owner_id UUID REFERENCES users(id);
ALTER TABLE commesse ADD COLUMN IF NOT EXISTS budget DECIMAL(15,2);
ALTER TABLE commesse ADD COLUMN IF NOT EXISTS data_inizio DATE;
ALTER TABLE commesse ADD COLUMN IF NOT EXISTS data_fine_prevista DATE;
ALTER TABLE commesse ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'active';
ALTER TABLE commesse ADD COLUMN IF NOT EXISTS sla_default_hours INTEGER DEFAULT 48;
ALTER TABLE commesse ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';
ALTER TABLE commesse ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE commesse ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Enhanced milestones
ALTER TABLE milestones ADD COLUMN IF NOT EXISTS commessa_id INTEGER REFERENCES commesse(id);
ALTER TABLE milestones ADD COLUMN IF NOT EXISTS auto_generate_tickets BOOLEAN DEFAULT true;
ALTER TABLE milestones ADD COLUMN IF NOT EXISTS warning_days INTEGER DEFAULT 2;
ALTER TABLE milestones ADD COLUMN IF NOT EXISTS escalation_days INTEGER DEFAULT 1;
ALTER TABLE milestones ADD COLUMN IF NOT EXISTS template_data JSONB DEFAULT '{}';

-- Task templates
CREATE TABLE IF NOT EXISTS modelli_task (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    descrizione TEXT,
    categoria VARCHAR(100),
    sla_hours INTEGER DEFAULT 24,
    priorita VARCHAR(50) DEFAULT 'medium',
    assignee_default_role VARCHAR(50),
    checklist JSONB DEFAULT '[]',
    template_content TEXT,
    tags JSONB DEFAULT '[]',
    created_by UUID REFERENCES users(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enhanced tickets
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS commessa_id INTEGER REFERENCES commesse(id);
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS sla_deadline TIMESTAMP;
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS priority VARCHAR(50) DEFAULT 'medium';
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';

-- Enhanced tasks
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS modello_task_id INTEGER REFERENCES modelli_task(id);
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS sla_hours INTEGER DEFAULT 24;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS sla_deadline TIMESTAMP;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS estimated_hours DECIMAL(5,2);
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS actual_hours DECIMAL(5,2);
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS parent_task_id INTEGER REFERENCES tasks(id);
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS checklist JSONB DEFAULT '[]';
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';

-- ==============================================
-- AUDIT AND TRACKING
-- ==============================================

-- Audit log
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id VARCHAR(100),
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SLA tracking
CREATE TABLE IF NOT EXISTS sla_tracking (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER NOT NULL,
    sla_deadline TIMESTAMP NOT NULL,
    warning_sent_at TIMESTAMP,
    escalation_sent_at TIMESTAMP,
    completed_at TIMESTAMP,
    is_breached BOOLEAN DEFAULT false,
    breach_duration INTERVAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- INDEXES FOR PERFORMANCE
-- ==============================================

CREATE INDEX IF NOT EXISTS idx_commesse_codice ON commesse(codice);
CREATE INDEX IF NOT EXISTS idx_commesse_client ON commesse(client_id);
CREATE INDEX IF NOT EXISTS idx_tickets_commessa ON tickets(commessa_id);
CREATE INDEX IF NOT EXISTS idx_tickets_sla ON tickets(sla_deadline);
CREATE INDEX IF NOT EXISTS idx_tasks_sla ON tasks(sla_deadline);
CREATE INDEX IF NOT EXISTS idx_sla_tracking_deadline ON sla_tracking(sla_deadline);

-- ==============================================
-- INITIAL DATA
-- ==============================================

-- System roles
INSERT INTO roles (name, description, permissions, is_system_role) VALUES
('admin', 'Administrator with full access', '{"all": true}', true),
('manager', 'Manager with team oversight', '{"read": ["all"], "write": ["tickets", "tasks"], "admin": ["users"]}', true),
('operator', 'Standard operator', '{"read": ["tickets", "tasks"], "write": ["tasks"]}', true),
('viewer', 'Read-only access', '{"read": ["tickets", "tasks"]}', true)
ON CONFLICT (name) DO NOTHING;

\echo '✅ Intelligence Platform v5.0 database schema enhanced successfully!'
\echo '🌐 Domain: intelligencehub.enduser-digital.com'
