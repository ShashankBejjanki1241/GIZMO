-- Gizmo AI Database Initialization

CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(255) UNIQUE NOT NULL,
    run_id VARCHAR(255) NOT NULL,
    template VARCHAR(100) NOT NULL,
    instruction TEXT NOT NULL,
    state VARCHAR(50) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    iteration INTEGER DEFAULT 0,
    current_agent VARCHAR(100),
    error TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS task_events (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(255) NOT NULL,
    run_id VARCHAR(255) NOT NULL,
    iteration INTEGER NOT NULL,
    stage VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    data JSONB,
    message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (task_id) REFERENCES tasks(task_id)
);

CREATE INDEX IF NOT EXISTS idx_tasks_task_id ON tasks(task_id);
CREATE INDEX IF NOT EXISTS idx_events_task_id ON task_events(task_id);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON task_events(timestamp);
