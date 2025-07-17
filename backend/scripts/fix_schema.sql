-- Fix Schema - UUID Consistency COMPLETE
-- ==============================================

-- Fix milestones: add commessa_id as UUID (correggiamo client_id che è INTEGER)
ALTER TABLE milestones ADD COLUMN IF NOT EXISTS commessa_id UUID REFERENCES commesse(id);

-- Fix tickets: add commessa_id as UUID
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS commessa_id UUID REFERENCES commesse(id);

-- Fix tasks: add parent_task_id as UUID
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS parent_task_id UUID REFERENCES tasks(id);

-- Fix modelli_task: già creato correttamente come UUID
-- Verifichiamo che esista
CREATE TABLE IF NOT EXISTS modelli_task (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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

-- Add missing columns to tickets
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS assigned_to UUID REFERENCES users(id);
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS activity_id UUID REFERENCES activities(id);

-- Create correct indexes
CREATE INDEX IF NOT EXISTS idx_milestones_commessa ON milestones(commessa_id);
CREATE INDEX IF NOT EXISTS idx_tickets_commessa ON tickets(commessa_id);
CREATE INDEX IF NOT EXISTS idx_tickets_assigned ON tickets(assigned_to);
CREATE INDEX IF NOT EXISTS idx_tasks_parent ON tasks(parent_task_id);
CREATE INDEX IF NOT EXISTS idx_tasks_modello ON tasks(modello_task_id);

-- Create modelli_ticket table with correct UUID references
CREATE TABLE IF NOT EXISTS modelli_ticket (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome VARCHAR(255) NOT NULL,
    descrizione TEXT,
    milestone_id UUID REFERENCES milestones(id),
    task_templates JSONB DEFAULT '[]',
    auto_assign_rules JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Nota: client_id in commesse è INTEGER che referenzia companies(id) 
-- che dovrebbe essere companies.id ma companies usa id SERIAL
-- Questo è corretto così come è

\echo '✅ Schema fixed with UUID consistency - COMPLETE!'
