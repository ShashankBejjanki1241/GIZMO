// Types for the enhanced Gizmo AI UI

export interface TaskEvent {
  task_id: string;
  run_id: string;
  iteration: number;
  stage: 'starting' | 'planning' | 'coding' | 'diff_applied' | 'testing' | 'test_report' | 'done' | 'failed';
  timestamp: number;
  data: any;
  message: string;
}

export interface Task {
  task_id: string;
  run_id: string;
  template: string;
  instruction: string;
  state: string;
  start_time: number;
  iteration: number;
  current_agent: string | null;
  error: string | null;
}

export interface SystemHealth {
  status: string;
  timestamp: number;
  uptime: number;
  version: string;
  service: string;
  services: {
    database: string;
    redis: string;
    orchestrator: string;
  };
  metrics: {
    total_requests: number;
    requests_per_minute: number;
    phase7_features: {
      memory_layer: {
        successful_plans: number;
        successful_diffs: number;
        task_patterns: Record<string, any>;
        max_memories: number;
      };
      reliability_metrics: {
        total_tasks: number;
        successful_tasks: number;
        failed_tasks: number;
        total_tokens: number;
        total_iterations: number;
        avg_time_to_first_event: number;
        avg_iterations_to_pass: number;
        retry_counts: Record<string, number>;
        failure_modes: Record<string, number>;
      };
    };
  };
}
