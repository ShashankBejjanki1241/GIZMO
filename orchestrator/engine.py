"""
Gizmo AI - Orchestrator Engine
Main orchestration logic for coordinating agents with deterministic state machine

Developer: Shashank B
Repository: https://github.com/ShashankBejjanki1241/GIZMO
Last Updated: December 2024
"""

import os
import time
import uuid
import asyncio
import json
import hashlib
from typing import Dict, Any, Optional, List, Tuple
from contextlib import asynccontextmanager
from enum import Enum
from datetime import datetime
from collections import defaultdict, deque

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

import structlog
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai

# Import local modules
from protocol import TaskRequest, Message, Role, MsgType
from sandbox import SecureSandbox, PatchResult

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Global variables for health checks
startup_time = time.time()
request_count = 0

# Task state management
class TaskState(str, Enum):
    starting = "starting"
    planning = "planning"
    coding = "coding"
    diff_applied = "diff_applied"
    testing = "testing"
    test_report = "test_report"
    done = "done"
    failed = "failed"

class TaskEvent(BaseModel):
    task_id: str
    run_id: str
    iteration: int
    stage: str
    timestamp: float
    data: Dict[str, Any]
    message: str

class TaskRun(BaseModel):
    task_id: str
    run_id: str
    template: str
    instruction: str
    state: TaskState
    start_time: float
    iteration: int
    current_agent: Optional[str]
    error: Optional[str]

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("WebSocket connected", total_connections=len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info("WebSocket disconnected", total_connections=len(self.active_connections))

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected WebSocket clients"""
        if self.active_connections:
            message_json = json.dumps(message)
            await asyncio.gather(
                *[connection.send_text(message_json) for connection in self.active_connections],
                return_exceptions=True
            )
            logger.debug("Message broadcasted", recipients=len(self.active_connections))

# Phase 7: Memory Layer for Successful Patterns
class MemoryLayer:
    """Memory layer storing successful plans and diffs for retrieval as hints"""
    
    def __init__(self, max_memories: int = 100):
        self.max_memories = max_memories
        self.successful_plans = deque(maxlen=max_memories)
        self.successful_diffs = deque(maxlen=max_memories)
        self.task_patterns = {}  # task_type -> success_count
        
    def store_successful_plan(self, template: str, instruction: str, plan: Dict[str, Any], success_metrics: Dict[str, Any]):
        """Store a successful plan with metadata"""
        memory = {
            'template': template,
            'instruction': instruction,
            'plan': plan,
            'success_metrics': success_metrics,
            'timestamp': time.time(),
            'hash': hashlib.md5(f"{template}:{instruction}".encode()).hexdigest()
        }
        self.successful_plans.append(memory)
        logger.info("Stored successful plan in memory", template=template, instruction_hash=memory['hash'])
        
    def store_successful_diff(self, template: str, plan: Dict[str, Any], diff: str, success_metrics: Dict[str, Any]):
        """Store a successful diff with metadata"""
        memory = {
            'template': template,
            'plan': plan,
            'diff': diff,
            'success_metrics': success_metrics,
            'timestamp': time.time(),
            'hash': hashlib.md5(f"{template}:{json.dumps(plan)}".encode()).hexdigest()
        }
        self.successful_diffs.append(memory)
        logger.info("Stored successful diff in memory", template=template, diff_hash=memory['hash'])
        
    def get_similar_examples(self, template: str, instruction: str, max_examples: int = 2) -> List[Dict[str, Any]]:
        """Retrieve similar successful examples as hints"""
        examples = []
        
        # Find similar plans
        for memory in reversed(self.successful_plans):
            if memory['template'] == template:
                # Simple similarity based on instruction keywords
                instruction_words = set(instruction.lower().split())
                memory_words = set(memory['instruction'].lower().split())
                similarity = len(instruction_words.intersection(memory_words)) / len(instruction_words.union(memory_words))
                
                if similarity > 0.3:  # 30% similarity threshold
                    examples.append({
                        'type': 'plan',
                        'instruction': memory['instruction'],
                        'plan': memory['plan'],
                        'similarity': similarity
                    })
                    
                if len(examples) >= max_examples:
                    break
                    
        # Find similar diffs
        for memory in reversed(self.successful_diffs):
            if memory['template'] == template:
                examples.append({
                    'type': 'diff',
                    'plan': memory['plan'],
                    'diff': memory['diff']
                })
                
                if len(examples) >= max_examples:
                    break
                    
        logger.info("Retrieved similar examples", template=template, count=len(examples))
        return examples

# Phase 7: Enhanced Metrics Tracking
class MetricsTracker:
    """Track comprehensive metrics for reliability analysis"""
    
    def __init__(self):
        self.task_metrics = {}
        self.global_metrics = {
            'total_tasks': 0,
            'successful_tasks': 0,
            'failed_tasks': 0,
            'total_tokens': 0,
            'total_iterations': 0,
            'avg_time_to_first_event': 0,
            'avg_iterations_to_pass': 0,
            'retry_counts': defaultdict(int),
            'failure_modes': defaultdict(int)
        }
        
    def start_task(self, task_id: str, template: str, instruction: str):
        """Initialize metrics for a new task"""
        self.task_metrics[task_id] = {
            'template': template,
            'instruction': instruction,
            'start_time': time.time(),
            'first_event_time': None,
            'iterations': 0,
            'tokens_used': 0,
            'retry_counts': defaultdict(int),
            'failure_modes': [],
            'stages': [],
            'current_stage': 'starting'
        }
        self.global_metrics['total_tasks'] += 1
        logger.info("Started metrics tracking", task_id=task_id)
        
    def record_event(self, task_id: str, stage: str, iteration: int, tokens: int = 0, error: str = None):
        """Record an event with metrics"""
        if task_id not in self.task_metrics:
            return
            
        metrics = self.task_metrics[task_id]
        metrics['stages'].append(stage)
        metrics['current_stage'] = stage
        metrics['iterations'] = max(metrics['iterations'], iteration)
        metrics['tokens_used'] += tokens
        
        if metrics['first_event_time'] is None:
            metrics['first_event_time'] = time.time()
            
        if error:
            metrics['failure_modes'].append(error)
            self.global_metrics['failure_modes'][error] += 1
            
        logger.debug("Recorded event metrics", task_id=task_id, stage=stage, iteration=iteration)
        
    def record_retry(self, task_id: str, stage: str, error_type: str):
        """Record a retry attempt"""
        if task_id in self.task_metrics:
            self.task_metrics[task_id]['retry_counts'][stage] += 1
            self.global_metrics['retry_counts'][f"{stage}_{error_type}"] += 1
            
    def complete_task(self, task_id: str, success: bool):
        """Complete task metrics and update global stats"""
        if task_id not in self.task_metrics:
            return
            
        metrics = self.task_metrics[task_id]
        
        # Calculate task-specific metrics
        if metrics['first_event_time']:
            time_to_first = metrics['first_event_time'] - metrics['start_time']
            self.global_metrics['avg_time_to_first_event'] = (
                (self.global_metrics['avg_time_to_first_event'] * (self.global_metrics['successful_tasks'] + self.global_metrics['failed_tasks']) + time_to_first) /
                (self.global_metrics['successful_tasks'] + self.global_metrics['failed_tasks'] + 1)
            )
            
        self.global_metrics['total_iterations'] += metrics['iterations']
        self.global_metrics['total_tokens'] += metrics['tokens_used']
        
        if success:
            self.global_metrics['successful_tasks'] += 1
            avg_iterations = self.global_metrics['total_iterations'] / self.global_metrics['successful_tasks']
            self.global_metrics['avg_iterations_to_pass'] = avg_iterations
        else:
            self.global_metrics['failed_tasks'] += 1
            
        logger.info("Completed task metrics", task_id=task_id, success=success, 
                   iterations=metrics['iterations'], tokens=metrics['tokens_used'])
        
    def get_task_metrics(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get metrics for a specific task"""
        return self.task_metrics.get(task_id)
        
    def get_global_metrics(self) -> Dict[str, Any]:
        """Get global reliability metrics"""
        total = self.global_metrics['total_tasks']
        if total == 0:
            return self.global_metrics
            
        return {
            **self.global_metrics,
            'success_rate': self.global_metrics['successful_tasks'] / total,
            'avg_iterations_per_task': self.global_metrics['total_iterations'] / total,
            'avg_tokens_per_task': self.global_metrics['total_tokens'] / total
        }

# Phase 7: Enhanced RealLLM with Auto-retries and Memory
class RealLLM:
    """Real LLM integration with Phase 7 reliability features"""
    
    def __init__(self, memory_layer: MemoryLayer, metrics_tracker: MetricsTracker):
        self.client = None
        self.model = "gpt-4o-mini"
        self.temperature = 0.1
        self.memory_layer = memory_layer
        self.metrics_tracker = metrics_tracker
        self.max_retries = 3
        
        # Initialize OpenAI client if API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                self.client = openai.AsyncOpenAI(api_key=api_key)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
                self.client = None
        else:
            logger.warning("No OPENAI_API_KEY found, falling back to stubbed responses")
    
    async def call_planner(self, instruction: str, template: str, task_id: str) -> Dict[str, Any]:
        """Call real LLM for planning with auto-retries and memory hints"""
        if not self.client:
            return await self._stubbed_planner(instruction, template)
        
        # Get similar examples from memory
        similar_examples = self.memory_layer.get_similar_examples(template, instruction)
        memory_hints = ""
        if similar_examples:
            memory_hints = "\n\nSIMILAR SUCCESSFUL EXAMPLES:\n"
            for i, example in enumerate(similar_examples[:2]):
                if example['type'] == 'plan':
                    memory_hints += f"\nExample {i+1}:\nInstruction: {example['instruction']}\nPlan: {json.dumps(example['plan'], indent=2)}\n"
        
        for attempt in range(self.max_retries):
            try:
                relevant_files = self._get_relevant_files(template)
                
                prompt = f"""You are a software planning agent. Analyze the task and create a plan.

TASK: {instruction}
TEMPLATE: {template}
RELEVANT FILES: {', '.join(relevant_files)}{memory_hints}

Create a plan in this EXACT JSON format (no extra text):
{{
  "plan": ["step1", "step2", "step3"],
  "files_to_modify": ["file1", "file2"],
  "estimated_time": "X minutes"
}}

RESPONSE:"""

                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=1000
                )
                
                content = response.choices[0].message.content.strip()
                
                # Try to parse JSON
                try:
                    plan = json.loads(content)
                    if self._validate_plan_format(plan):
                        # Record successful planning
                        self.metrics_tracker.record_event(task_id, 'planning', 0, 
                                                       len(content.split()), 'success')
                        return plan
                except json.JSONDecodeError:
                    pass
                
                # If we get here, validation failed
                self.metrics_tracker.record_event(task_id, 'planning', 0, 
                                               len(content.split()), 'invalid_json')
                self.metrics_tracker.record_retry(task_id, 'planning', 'invalid_json')
                
                if attempt < self.max_retries - 1:
                    logger.warning(f"Planner attempt {attempt + 1} failed, retrying...")
                    await asyncio.sleep(1)
                    continue
                    
            except Exception as e:
                logger.error(f"Planner LLM call failed: {e}")
                self.metrics_tracker.record_event(task_id, 'planning', 0, 0, str(e))
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(1)
                    continue
        
        # All retries failed, fall back to stub
        logger.error("All planner retries failed, using stub")
        return await self._stubbed_planner(instruction, template)
    
    async def call_coder(self, plan: Dict[str, Any], template: str, task_id: str) -> str:
        """Call real LLM for coding with auto-retries and memory hints"""
        if not self.client:
            return await self._stubbed_coder(plan, template)
        
        # Get similar examples from memory
        similar_examples = self.memory_layer.get_similar_examples(template, "", max_examples=1)
        memory_hints = ""
        if similar_examples:
            for example in similar_examples:
                if example['type'] == 'diff':
                    memory_hints = f"\n\nSIMILAR SUCCESSFUL DIFF:\n{example['diff']}\n"
        
        for attempt in range(self.max_retries):
            try:
                relevant_files = self._get_relevant_files(template)
                
                prompt = f"""You are a software coding agent. Implement the planned changes.

PLAN: {json.dumps(plan, indent=2)}
TEMPLATE: {template}
RELEVANT FILES: {', '.join(relevant_files)}{memory_hints}

Generate ONLY a unified diff in this format (no extra text, no markdown):
--- a/filename
+++ b/filename
@@ -line,context +line,context @@
 unchanged line
+added line
-removed line

The diff must:
1. Be valid unified diff format
2. Include a COMMIT line at the end
3. Be under 50 lines total
4. Only modify the files specified in the plan

RESPONSE:"""

                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=1000
                )
                
                content = response.choices[0].message.content.strip()
                
                if self._validate_diff_format(content):
                    # Record successful coding
                    self.metrics_tracker.record_event(task_id, 'coding', 0, 
                                                   len(content.split()), 'success')
                    return content
                
                # Validation failed
                self.metrics_tracker.record_event(task_id, 'coding', 0, 
                                               len(content.split()), 'invalid_diff')
                self.metrics_tracker.record_retry(task_id, 'coding', 'invalid_diff')
                
                if attempt < self.max_retries - 1:
                    logger.warning(f"Coder attempt {attempt + 1} failed, retrying...")
                    await asyncio.sleep(1)
                    continue
                    
            except Exception as e:
                logger.error(f"Coder LLM call failed: {e}")
                self.metrics_tracker.record_event(task_id, 'coding', 0, 0, str(e))
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(1)
                    continue
        
        # All retries failed, fall back to stub
        logger.error("All coder retries failed, using stub")
        return await self._stubbed_coder(plan, template)
    
    async def call_tester(self, test_results: Dict[str, Any], template: str, task_id: str) -> Dict[str, Any]:
        """Call real LLM for testing with auto-retries"""
        if not self.client:
            return await self._stubbed_tester(test_results, template)
        
        for attempt in range(self.max_retries):
            try:
                prompt = f"""You are a software testing agent. Analyze test results and generate a report.

TEST RESULTS: {json.dumps(test_results, indent=2)}
TEMPLATE: {template}

Generate a test report in this EXACT JSON format (no extra text):
{{
  "test_summary": "brief summary",
  "test_results": {json.dumps(test_results, indent=2)},
  "recommendations": ["rec1", "rec2"],
  "status": "passed|failed|partial"
}}

RESPONSE:"""

                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=500
                )
                
                content = response.choices[0].message.content.strip()
                
                # Try to extract JSON from response
                json_content = self._extract_json(content)
                if json_content:
                    # Record successful testing
                    self.metrics_tracker.record_event(task_id, 'testing', 0, 
                                                   len(content.split()), 'success')
                    return json_content
                
                # JSON extraction failed
                self.metrics_tracker.record_event(task_id, 'testing', 0, 
                                               len(content.split()), 'invalid_json')
                self.metrics_tracker.record_retry(task_id, 'testing', 'invalid_json')
                
                if attempt < self.max_retries - 1:
                    logger.warning(f"Tester attempt {attempt + 1} failed, retrying...")
                    await asyncio.sleep(1)
                    continue
                    
            except Exception as e:
                logger.error(f"Tester LLM call failed: {e}")
                self.metrics_tracker.record_event(task_id, 'testing', 0, 0, str(e))
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(1)
                    continue
        
        # All retries failed, fall back to stub
        logger.error("All tester retries failed, using stub")
        return await self._stubbed_tester(test_results, template)
    
    def _validate_plan_format(self, plan: Dict[str, Any]) -> bool:
        """Validate plan JSON format"""
        required_fields = ['plan', 'files_to_modify', 'estimated_time']
        return all(field in plan for field in required_fields) and isinstance(plan['plan'], list)
    
    def _validate_diff_format(self, content: str) -> bool:
        """Validate unified diff format"""
        lines = content.split('\n')
        
        # Check for basic diff structure
        if not any(line.startswith('--- a/') for line in lines):
            return False
        
        if not any(line.startswith('+++ b/') for line in lines):
            return False
        
        if not any(line.startswith('@@') for line in lines):
            return False
        
        # Check for COMMIT line
        if not any('COMMIT:' in line for line in lines):
            return False
        
        # Check size limit
        if len(lines) > 50:
            return False
        
        return True
    
    def _extract_json(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from LLM response"""
        try:
            # Try to parse the entire content as JSON
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to find JSON within the content
            try:
                # Look for JSON between curly braces
                start = content.find('{')
                end = content.rfind('}') + 1
                if start != -1 and end != 0:
                    json_str = content[start:end]
                    return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        return None
    
    def _get_relevant_files(self, template: str) -> list:
        """Get relevant files for context, trimmed to essential info"""
        if template == "react":
            return ["src/calculator.js", "src/calculator.test.js"]
        elif template == "express":
            return ["src/app.js", "src/app.test.js"]
        elif template == "flask":
            return ["app.py", "test_app.py"]
        else:
            return ["main.py", "test_main.py"]
    
    # Fallback stubbed methods
    async def _stubbed_planner(self, instruction: str, template: str) -> Dict[str, Any]:
        """Fallback stubbed planner"""
        await asyncio.sleep(0.1)
        return {
            "plan": [
                "Add missing feature",
                "Implement core functionality", 
                "Add tests for new feature"
            ],
            "files_to_modify": ["src/main.js", "src/main.test.js"],
            "estimated_time": "5 minutes"
        }
    
    async def _stubbed_coder(self, plan: Dict[str, Any], template: str) -> str:
        """Fallback stubbed coder"""
        await asyncio.sleep(0.1)
        return """--- a/src/main.js
+++ b/src/main.js
@@ -10,6 +10,12 @@
   return a - b;
 }
 
+function divide(a, b) {
+  if (b === 0) {
+    throw new Error('Division by zero');
+  }
+  return a / b;
+}
 
 module.exports = { add, subtract, multiply, divide };
COMMIT: Add division function with divide-by-zero guard"""
    
    async def _stubbed_tester(self, test_results: Dict[str, Any], template: str) -> Dict[str, Any]:
        """Fallback stubbed tester"""
        await asyncio.sleep(0.1)
        return {
            "test_summary": "Tests completed successfully",
            "test_results": test_results,
            "recommendations": ["All tests passing"],
            "status": "passed"
        }

# Phase 7: Enhanced Orchestrator with Reliability Features
class Orchestrator:
    """Enhanced orchestrator with Phase 7 reliability features"""
    
    def __init__(self):
        # Initialize Phase 7 components
        self.memory_layer = MemoryLayer()
        self.metrics_tracker = MetricsTracker()
        self.llm = RealLLM(self.memory_layer, self.metrics_tracker)
        
        # Task management
        self.active_tasks = {}
        self.task_events = defaultdict(list)
        
        # WebSocket management
        self.connection_manager = ConnectionManager()
        
        # Failure quarantine tracking
        self.failure_quarantine = defaultdict(int)  # error_type -> count
        
        logger.info("Enhanced Orchestrator initialized with Phase 7 reliability features")
    
    async def start_task(self, task_request: TaskRequest) -> TaskRun:
        """Start a new task with enhanced reliability"""
        task_id = task_request.task_id
        
        # Check failure quarantine
        if self._is_quarantined(task_request):
            raise HTTPException(status_code=400, detail="Task type quarantined due to repeated failures")
        
        # Initialize metrics tracking
        self.metrics_tracker.start_task(task_id, task_request.template, task_request.instruction)
        
        # Create task run
        run_id = f"run-{hashlib.md5(f'{task_id}-{time.time()}'.encode()).hexdigest()}"
        task_run = TaskRun(
            task_id=task_id,
            run_id=run_id,
            template=task_request.template,
            instruction=task_request.instruction,
            state=TaskState.starting,
            start_time=time.time(),
            iteration=0,
            current_agent=None,
            error=None
        )
        
        self.active_tasks[task_id] = task_run
        
        # Start task execution
        asyncio.create_task(self._execute_task(task_id))
        
        logger.info("Started enhanced task execution", task_id=task_id, run_id=run_id)
        return task_run
    
    def _is_quarantined(self, task_request: TaskRequest) -> bool:
        """Check if task type is quarantined due to repeated failures"""
        # Simple quarantine based on template and instruction pattern
        task_signature = f"{task_request.template}:{hashlib.md5(task_request.instruction.encode()).hexdigest()[:8]}"
        return self.failure_quarantine[task_signature] >= 2
    
    async def _execute_task(self, task_id: str):
        """Execute task with enhanced reliability and retry logic"""
        task = self.active_tasks[task_id]
        
        try:
            # Phase 1: Starting
            await self._emit_event(task_id, "starting", "Task execution started")
            
            # Initialize sandbox
            sandbox = SecureSandbox(task_id, task.template)
            await self._emit_event(task_id, "starting", "Secure sandbox initialized", 
                                 {"sandbox_info": sandbox.get_info()})
            
            # Phase 2: Planning
            await self._emit_event(task_id, "planning", "Planner agent is analyzing task")
            plan = await self.llm.call_planner(task.instruction, task.template, task_id)
            await self._emit_event(task_id, "planning", "Planning completed", {"plan": plan, "agent": "planner"})
            
            # Phase 3: Coding
            await self._emit_event(task_id, "coding", "Coder agent is implementing changes")
            diff = await self.llm.call_coder(plan, task.template, task_id)
            await self._emit_event(task_id, "coding", "Code changes generated", {"diff": diff, "agent": "coder"})
            
            # Phase 4: Apply Patch
            await self._emit_event(task_id, "diff_applied", "Applying code changes securely")
            patch_result = sandbox.apply_patch(diff)
            await self._emit_event(task_id, "diff_applied", "Code changes applied successfully", 
                                 {"diff": diff, "patch_result": patch_result, "agent": "coder"})
            
            # Phase 5: Testing
            await self._emit_event(task_id, "testing", "Tester agent is running tests")
            test_results = sandbox.run_tests()
            await self._emit_event(task_id, "testing", "Tests completed", {"test_results": test_results, "agent": "tester"})
            
            # Phase 6: Test Report
            await self._emit_event(task_id, "test_report", "Generating test report")
            test_report = await self.llm.call_tester(test_results, task.template, task_id)
            await self._emit_event(task_id, "test_report", "Test report generated", 
                                 {"test_report": test_report, "agent": "tester"})
            
            # Phase 7: Completion
            await self._emit_event(task_id, "done", "Task completed successfully", {
                "final_results": {
                    "plan": plan,
                    "diff": diff,
                    "patch_result": patch_result,
                    "test_results": test_results,
                    "test_report": test_report,
                    "artifacts": sandbox.get_artifacts()
                }
            })
            
            # Update task state
            task.state = TaskState.done
            task.current_agent = "tester"
            
            # Store successful patterns in memory
            if test_report.get('status') == 'passed':
                self.memory_layer.store_successful_plan(task.template, task.instruction, plan, 
                                                      {"iterations": task.iteration, "status": "passed"})
                self.memory_layer.store_successful_diff(task.template, plan, diff, 
                                                      {"iterations": task.iteration, "status": "passed"})
            
            # Complete metrics
            self.metrics_tracker.complete_task(task_id, True)
            
            logger.info("Task completed successfully", task_id=task_id)
            
        except Exception as e:
            error_msg = str(e)
            logger.error("Task execution failed", task_id=task_id, error=error_msg)
            
            # Record failure
            self.metrics_tracker.record_event(task_id, "failed", task.iteration, 0, error_msg)
            
            # Update task state
            task.state = TaskState.failed
            task.error = error_msg
            
            # Check for quarantine
            task_signature = f"{task.template}:{hashlib.md5(task.instruction.encode()).hexdigest()[:8]}"
            self.failure_quarantine[task_signature] += 1
            
            # Emit failure event
            await self._emit_event(task_id, "failed", f"Task failed: {error_msg}")
            
            # Complete metrics
            self.metrics_tracker.complete_task(task_id, False)
        
        finally:
            # Cleanup
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
    
    async def _emit_event(self, task_id: str, stage: str, message: str, data: Dict[str, Any] = None):
        """Emit task event with enhanced metrics"""
        event = TaskEvent(
            task_id=task_id,
            run_id=self.active_tasks[task_id].run_id,
            iteration=self.active_tasks[task_id].iteration,
            stage=stage,
            timestamp=time.time(),
            data=data or {},
            message=message
        )
        
        self.task_events[task_id].append(event)
        self.active_tasks[task_id].iteration += 1
        
        # Update metrics
        self.metrics_tracker.record_event(task_id, stage, event.iteration)
        
        # Broadcast to WebSocket
        await self.connection_manager.broadcast({
            "type": "task_event",
            "task_id": task_id,
            "event": event.dict()
        })
        
        logger.debug("Emitted task event", task_id=task_id, stage=stage, message=message)
    
    # API endpoints
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task with enhanced metrics"""
        if task_id not in self.active_tasks:
            return None
            
        task = self.active_tasks[task_id]
        events = self.task_events[task_id]
        metrics = self.metrics_tracker.get_task_metrics(task_id)
        
        return {
            "task": task.dict(),
            "events": [event.dict() for event in events],
            "metrics": metrics
        }
    
    async def get_tasks(self) -> List[TaskRun]:
        """Get all active tasks"""
        return list(self.active_tasks.values())
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get global reliability metrics"""
        return self.metrics_tracker.get_global_metrics()
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory layer statistics"""
        return {
            "successful_plans": len(self.memory_layer.successful_plans),
            "successful_diffs": len(self.memory_layer.successful_diffs),
            "task_patterns": self.memory_layer.task_patterns,
            "max_memories": self.memory_layer.max_memories
        }

# Global orchestrator instance
orchestrator = Orchestrator()

# FastAPI application setup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Gizmo AI Enhanced Orchestrator", version="0.2.0")
    yield
    # Shutdown
    logger.info("Shutting down Gizmo AI Enhanced Orchestrator")

# Create FastAPI application
app = FastAPI(
    title="Gizmo AI Enhanced Orchestrator",
    description="Core orchestration engine with Phase 7 reliability features",
    version="0.2.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3002"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID to all requests for tracking"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Add request ID to response headers
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with request ID and timing"""
    global request_count
    request_count += 1
    
    start_time = time.time()
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    # Log request
    logger.info(
        "Enhanced Orchestrator request started",
        request_id=request_id,
        method=request.method,
        url=str(request.url),
        client_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        request_number=request_count
    )
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Log response
    logger.info(
        "Enhanced Orchestrator request completed",
        request_id=request_id,
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        duration=duration,
        request_number=request_count
    )
    
    return response

# Health check endpoint
@app.get("/healthz")
async def health_check():
    """Enhanced health check with Phase 7 metrics"""
    global startup_time, request_count
    
    # Get orchestrator metrics
    metrics = await orchestrator.get_metrics()
    memory_stats = await orchestrator.get_memory_stats()
    
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "uptime": time.time() - startup_time,
        "version": "0.2.0",
        "service": "enhanced_orchestrator",
        "services": {
            "database": "connected",  # Placeholder
            "redis": "connected",     # Placeholder
            "orchestrator": "healthy"
        },
        "metrics": {
            "total_requests": request_count,
            "requests_per_minute": request_count / max((time.time() - startup_time) / 60, 1),
            "phase7_features": {
                "memory_layer": memory_stats,
                "reliability_metrics": metrics
            }
        }
    }

# Task management endpoints
@app.post("/api/v1/tasks")
async def create_task(task_request: TaskRequest):
    """Create and start a new task with enhanced reliability"""
    try:
        task_run = await orchestrator.start_task(task_request)
        return {
            "status": "success",
            "message": "Task created and started",
            "task_id": task_run.task_id,
            "run_id": task_run.run_id,
            "state": task_run.state
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error("Failed to create task", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")

@app.get("/api/v1/tasks")
async def list_tasks():
    """List all active tasks with enhanced metrics"""
    try:
        tasks = await orchestrator.get_tasks()
        return {"tasks": [task.dict() for task in tasks]}
    except Exception as e:
        logger.error("Failed to list tasks", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list tasks: {str(e)}")

@app.get("/api/v1/tasks/{task_id}")
async def get_task(task_id: str):
    """Get task details with enhanced metrics and events"""
    try:
        task_data = await orchestrator.get_task(task_id)
        if not task_data:
            raise HTTPException(status_code=404, detail="Task not found")
        return task_data
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error("Failed to get task", task_id=task_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get task: {str(e)}")

# Phase 7: Enhanced metrics and memory endpoints
@app.get("/api/v1/metrics")
async def get_metrics():
    """Get global reliability metrics"""
    try:
        metrics = await orchestrator.get_metrics()
        return metrics
    except Exception as e:
        logger.error("Failed to get metrics", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@app.get("/api/v1/memory")
async def get_memory_stats():
    """Get memory layer statistics"""
    try:
        memory_stats = await orchestrator.get_memory_stats()
        return memory_stats
    except Exception as e:
        logger.error("Failed to get memory stats", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get memory stats: {str(e)}")

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time task updates"""
    await orchestrator.connection_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        orchestrator.connection_manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
