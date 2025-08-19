-- Gizmo AI - PostgreSQL Initialization
-- This script sets up the initial database schema

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS orchestrator;
CREATE SCHEMA IF NOT EXISTS api;
CREATE SCHEMA IF NOT EXISTS audit;

-- Create audit log table
CREATE TABLE IF NOT EXISTS audit.logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    level VARCHAR(10) NOT NULL,
    logger_name VARCHAR(255),
    message TEXT NOT NULL,
    request_id VARCHAR(255),
    user_id VARCHAR(255),
    service_name VARCHAR(100),
    metadata JSONB
);

-- Create index on timestamp for efficient querying
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit.logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_logs_request_id ON audit.logs(request_id);

-- Create orchestrator tables
CREATE TABLE IF NOT EXISTS orchestrator.tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    metadata JSONB,
    result JSONB,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS orchestrator.agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'idle',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_heartbeat TIMESTAMPTZ,
    metadata JSONB
);

CREATE TABLE IF NOT EXISTS orchestrator.agent_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID REFERENCES orchestrator.tasks(id),
    agent_id UUID REFERENCES orchestrator.agents(id),
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    status VARCHAR(50) NOT NULL DEFAULT 'running',
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    execution_time_ms INTEGER
);

-- Create API tables
CREATE TABLE IF NOT EXISTS api.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS api.sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES api.users(id),
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_tasks_status ON orchestrator.tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON orchestrator.tasks(created_at);
CREATE INDEX IF NOT EXISTS idx_agent_executions_task_id ON orchestrator.agent_executions(task_id);
CREATE INDEX IF NOT EXISTS idx_users_username ON api.users(username);
CREATE INDEX IF NOT EXISTS idx_sessions_token ON api.sessions(session_token);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_tasks_updated_at 
    BEFORE UPDATE ON orchestrator.tasks 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON api.users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert initial data
INSERT INTO orchestrator.agents (name, type, status, metadata) VALUES
    ('planner-001', 'planner', 'idle', '{"version": "0.1.0", "capabilities": ["task_planning"]}'),
    ('coder-001', 'coder', 'idle', '{"version": "0.1.0", "capabilities": ["code_generation"]}'),
    ('tester-001', 'tester', 'idle', '{"version": "0.1.0", "capabilities": ["test_execution"]}')
ON CONFLICT DO NOTHING;

-- Grant permissions
GRANT USAGE ON SCHEMA orchestrator TO gizmo_user;
GRANT USAGE ON SCHEMA api TO gizmo_user;
GRANT USAGE ON SCHEMA audit TO gizmo_user;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA orchestrator TO gizmo_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA api TO gizmo_user;
GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA audit TO gizmo_user;

GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA orchestrator TO gizmo_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA api TO gizmo_user;

-- Create a view for task status
CREATE OR REPLACE VIEW orchestrator.task_status AS
SELECT 
    t.id,
    t.task_type,
    t.status,
    t.created_at,
    t.started_at,
    t.completed_at,
    COUNT(ae.id) as total_executions,
    COUNT(CASE WHEN ae.status = 'completed' THEN 1 END) as completed_executions,
    COUNT(CASE WHEN ae.status = 'failed' THEN 1 END) as failed_executions
FROM orchestrator.tasks t
LEFT JOIN orchestrator.agent_executions ae ON t.id = ae.task_id
GROUP BY t.id, t.task_type, t.status, t.created_at, t.started_at, t.completed_at;

GRANT SELECT ON orchestrator.task_status TO gizmo_user;
