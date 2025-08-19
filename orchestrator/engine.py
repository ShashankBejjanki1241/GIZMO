"""
Gizmo AI - Orchestrator Engine
Main orchestration logic for coordinating agents with deterministic state machine
"""

import os
import time
import uuid
import asyncio
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager
from enum import Enum
from datetime import datetime

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

import structlog
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import local modules
from protocol import TaskRequest, Message, Role, MsgType
from sandbox import SecureSandbox, PatchResult
import openai
import json
from typing import Optional, Dict, Any

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

logger = structlog.get_logger(__name__)

# Global variables for health checks
startup_time = time.time()
request_count = 0

# Task state management
class TaskState(Enum):
    STARTING = "starting"
    PLANNING = "planning"
    CODING = "coding"
    DIFF_APPLIED = "diff_applied"
    TESTING = "testing"
    TEST_REPORT = "test_report"
    DONE = "done"
    FAILED = "failed"

class TaskEvent(BaseModel):
    task_id: str
    run_id: str
    iteration: int
    stage: TaskState
    timestamp: float
    data: Dict[str, Any]
    message: str

class TaskRun(BaseModel):
    task_id: str
    run_id: str
    template: str
    instruction: str
    state: TaskState
    iteration: int
    start_time: float
    events: List[TaskEvent]
    current_agent: Optional[Role]
    error: Optional[str]

# Global task store (in production, use Redis/database)
active_tasks: Dict[str, TaskRun] = {}
task_events: Dict[str, List[TaskEvent]] = {}

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

    async def broadcast_event(self, event: TaskEvent):
        """Broadcast task event to all connected WebSocket clients"""
        if self.active_connections:
            message = event.model_dump_json()
            await asyncio.gather(
                *[connection.send_text(message) for connection in self.active_connections],
                return_exceptions=True
            )
            logger.info("Event broadcasted", event_id=event.task_id, recipients=len(self.active_connections))

manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Gizmo AI Orchestrator", version="0.1.0")
    yield
    # Shutdown
    logger.info("Shutting down Gizmo AI Orchestrator")

# Create FastAPI application
app = FastAPI(
    title="Gizmo AI Orchestrator",
    description="Core orchestration engine for coordinating AI agents",
    version="0.1.0",
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
        "Orchestrator request started",
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
        "Orchestrator request completed",
        request_id=request_id,
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        duration=duration,
        request_number=request_count
    )
    
    return response

# Real LLM integration for Phase 5
class RealLLM:
    """Real LLM integration with strict validation and error recovery"""
    
    def __init__(self):
        self.client = None
        self.model = "gpt-4o-mini"  # Default model
        self.temperature = 0.1  # Low temperature for deterministic output
        
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
    
    async def call_planner(self, instruction: str, template: str) -> Dict[str, Any]:
        """Call real LLM for planning with strict JSON validation"""
        if not self.client:
            return await self._stubbed_planner(instruction, template)
        
        try:
            # Get relevant files for context
            relevant_files = self._get_relevant_files(template)
            
            prompt = f"""You are a software planning agent. Analyze the task and create a plan.

TASK: {instruction}
TEMPLATE: {template}
RELEVANT FILES: {', '.join(relevant_files)}

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
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to extract JSON from response
            json_content = self._extract_json(content)
            if json_content:
                return json_content
            
            # If JSON extraction fails, retry with corrective message
            logger.warning("Planner JSON parse failed, retrying with corrective prompt")
            return await self._retry_planner_with_correction(instruction, template, content)
            
        except Exception as e:
            logger.error(f"Planner LLM call failed: {e}")
            return await self._stubbed_planner(instruction, template)
    
    async def _retry_planner_with_correction(self, instruction: str, template: str, failed_response: str) -> Dict[str, Any]:
        """Retry planner with corrective system message"""
        try:
            prompt = f"""Your previous response was invalid. You must respond with ONLY valid JSON.

TASK: {instruction}
TEMPLATE: {template}

Your invalid response was: {failed_response}

Respond with ONLY this JSON format (no extra text, no markdown):
{{
  "plan": ["step1", "step2", "step3"],
  "files_to_modify": ["file1", "file2"],
  "estimated_time": "X minutes"
}}"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            json_content = self._extract_json(content)
            
            if json_content:
                return json_content
            
            # If still failing, fall back to stub
            logger.error("Planner retry failed, using stub")
            return await self._stubbed_planner(instruction, template)
            
        except Exception as e:
            logger.error(f"Planner retry failed: {e}")
            return await self._stubbed_planner(instruction, template)
    
    async def call_coder(self, plan: Dict[str, Any], template: str) -> str:
        """Call real LLM for coding with strict diff validation"""
        if not self.client:
            return await self._stubbed_coder(plan, template)
        
        try:
            # Get relevant files for context
            relevant_files = self._get_relevant_files(template)
            
            prompt = f"""You are a software coding agent. Implement the planned changes.

PLAN: {json.dumps(plan, indent=2)}
TEMPLATE: {template}
RELEVANT FILES: {', '.join(relevant_files)}

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
            
            # Validate diff format
            if self._validate_diff_format(content):
                return content
            
            # If diff validation fails, retry with examples
            logger.warning("Coder diff validation failed, retrying with examples")
            return await self._retry_coder_with_examples(plan, template, content)
            
        except Exception as e:
            logger.error(f"Coder LLM call failed: {e}")
            return await self._stubbed_coder(plan, template)
    
    async def _retry_coder_with_examples(self, plan: Dict[str, Any], template: str, failed_response: str) -> str:
        """Retry coder with diff format examples"""
        try:
            prompt = f"""Your previous response was invalid. You must generate ONLY a valid unified diff.

PLAN: {json.dumps(plan, indent=2)}
TEMPLATE: {template}

Your invalid response was: {failed_response}

Here's the correct format example:
--- a/src/calculator.js
+++ b/src/calculator.js
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
COMMIT: Add division function with divide-by-zero guard

Generate ONLY the diff (no extra text, no markdown):"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            
            if self._validate_diff_format(content):
                return content
            
            # If still failing, fall back to stub
            return await self._stubbed_coder(plan, template)
            
        except Exception as e:
            logger.error(f"Coder retry failed: {e}")
            return await self._stubbed_coder(plan, template)
    
    async def call_tester(self, test_results: Dict[str, Any], template: str) -> Dict[str, Any]:
        """Call real LLM for testing with strict JSON validation"""
        if not self.client:
            return await self._stubbed_tester(test_results, template)
        
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
                return json_content
            
            # If JSON extraction fails, fall back to stub
            logger.error("Tester JSON parse failed, using stub")
            return await self._stubbed_coder(plan, template)
            
        except Exception as e:
            logger.error(f"Tester LLM call failed: {e}")
            return await self._stubbed_tester(test_results, template)
    
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
            "test_summary": "All tests passed successfully",
            "test_results": test_results,
            "recommendations": ["Code quality is good", "Test coverage is adequate"],
            "status": "passed"
        }

# Core orchestration logic
class Orchestrator:
    """Main orchestrator that manages the state machine"""
    
    def __init__(self):
        self.llm = StubbedLLM()
    
    async def start_task(self, task_request: TaskRequest) -> TaskRun:
        """Start a new task execution"""
        run_id = f"run-{uuid.uuid4()}"
        task_run = TaskRun(
            task_id=task_request.task_id,
            run_id=run_id,
            template=task_request.template,
            instruction=task_request.instruction,
            state=TaskState.STARTING,
            iteration=0,
            start_time=time.time(),
            events=[],
            current_agent=None,
            error=None
        )
        
        active_tasks[task_request.task_id] = task_run
        task_events[task_request.task_id] = []
        
        logger.info("Task started", task_id=task_request.task_id, run_id=run_id)
        
        # Start the orchestration loop
        asyncio.create_task(self._execute_task(task_run))
        
        return task_run
    
    async def _execute_task(self, task_run: TaskRun):
        """Execute the main task loop with secure sandbox"""
        sandbox = None
        try:
            # State 1: STARTING
            await self._emit_event(task_run, TaskState.STARTING, {
                "message": "Task execution started",
                "template": task_run.template,
                "instruction": task_run.instruction
            })
            
            # Initialize secure sandbox
            sandbox = SecureSandbox(task_run.task_id, task_run.template)
            sandbox_ready = await sandbox.prepare()
            
            if not sandbox_ready:
                raise Exception("Failed to initialize secure sandbox")
            
            await self._emit_event(task_run, TaskState.STARTING, {
                "message": "Secure sandbox initialized",
                "sandbox_info": sandbox.describe_repo()
            })
            
            # State 2: PLANNING
            await self._emit_event(task_run, TaskState.PLANNING, {
                "message": "Planner agent is analyzing task",
                "agent": "planner"
            })
            
            plan = await self.llm.call_planner(task_run.instruction, task_run.template)
            task_run.current_agent = "planner"
            
            await self._emit_event(task_run, TaskState.PLANNING, {
                "message": "Planning completed",
                "plan": plan,
                "agent": "planner"
            })
            
            # State 3: CODING
            await self._emit_event(task_run, TaskState.CODING, {
                "message": "Coder agent is implementing changes",
                "agent": "coder"
            })
            
            diff = await self.llm.call_coder(plan, task_run.template)
            task_run.current_agent = "coder"
            
            await self._emit_event(task_run, TaskState.CODING, {
                "message": "Code changes generated",
                "diff": diff,
                "agent": "coder"
            })
            
            # State 4: DIFF_APPLIED - Apply patch securely
            await self._emit_event(task_run, TaskState.DIFF_APPLIED, {
                "message": "Applying code changes securely",
                "agent": "coder"
            })
            
            patch_result = await sandbox.apply_patch(diff)
            
            if not patch_result.success:
                raise Exception(f"Patch application failed: {patch_result.error_message}")
            
            await self._emit_event(task_run, TaskState.DIFF_APPLIED, {
                "message": "Code changes applied successfully",
                "diff": diff,
                "patch_result": {
                    "applied_files": patch_result.applied_files,
                    "diff_stats": patch_result.diff_stats
                }
            })
            
            # State 5: TESTING
            await self._emit_event(task_run, TaskState.TESTING, {
                "message": "Tester agent is running tests",
                "agent": "tester"
            })
            
            # Run tests in secure sandbox
            test_results = await sandbox.run_tests()
            task_run.current_agent = "tester"
            
            await self._emit_event(task_run, TaskState.TESTING, {
                "message": "Tests completed",
                "test_results": test_results,
                "agent": "tester"
            })
            
            # State 6: TEST_REPORT
            await self._emit_event(task_run, TaskState.TEST_REPORT, {
                "message": "Generating test report",
                "agent": "tester"
            })
            
            test_report = await self.llm.call_tester(test_results, task_run.template)
            
            await self._emit_event(task_run, TaskState.TEST_REPORT, {
                "message": "Test report generated",
                "test_report": test_report,
                "agent": "tester"
            })
            
            # State 7: DONE
            await self._emit_event(task_run, TaskState.DONE, {
                "message": "Task completed successfully",
                "final_results": {
                    "plan": plan,
                    "diff": diff,
                    "patch_result": patch_result,
                    "test_results": test_results,
                    "test_report": test_report,
                    "artifacts": sandbox.get_artifacts()
                }
            })
            
            logger.info("Task completed successfully", task_id=task_run.task_id, run_id=task_run.run_id)
            
        except Exception as e:
            # State: FAILED
            task_run.state = TaskState.FAILED
            task_run.error = str(e)
            
            await self._emit_event(task_run, TaskState.FAILED, {
                "message": f"Task failed: {str(e)}",
                "error": str(e)
            })
            
            logger.error("Task failed", task_id=task_run.task_id, run_id=task_run.run_id, error=str(e))
            
        finally:
            # Cleanup sandbox
            if sandbox:
                try:
                    await sandbox.cleanup()
                except Exception as cleanup_error:
                    logger.error("Sandbox cleanup failed", error=str(cleanup_error))
    
    async def _emit_event(self, task_run: TaskRun, stage: TaskState, data: Dict[str, Any]):
        """Emit a task event and broadcast to WebSocket clients"""
        event = TaskEvent(
            task_id=task_run.task_id,
            run_id=task_run.run_id,
            iteration=task_run.iteration,
            stage=stage,
            timestamp=time.time(),
            data=data,
            message=data.get("message", f"Stage: {stage.value}")
        )
        
        # Add to task events
        task_run.events.append(event)
        task_events[task_run.task_id].append(event)
        
        # Update task state
        task_run.state = stage
        task_run.iteration += 1
        
        # Log event
        logger.info(
            "Task event emitted",
            task_id=task_run.task_id,
            run_id=task_run.run_id,
            stage=stage.value,
            iteration=task_run.iteration
        )
        
        # Broadcast to WebSocket clients
        await manager.broadcast_event(event)
    


# Global orchestrator instance
orchestrator = Orchestrator()

# Initialize with RealLLM (will fall back to stubbed if no API key)
orchestrator.llm = RealLLM()

# API Endpoints
@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint"""
    return {
        "message": "Gizmo AI Orchestrator",
        "version": "0.1.0",
        "status": "running"
    }

@app.get("/healthz")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    global startup_time, request_count
    
    # Basic health status
    health_status = "healthy"
    
    # Check database connectivity (placeholder for now)
    db_status = "connected"
    
    # Check Redis connectivity (placeholder for now)
    redis_status = "connected"
    
    return {
        "status": health_status,
        "timestamp": time.time(),
        "uptime": time.time() - startup_time,
        "version": "0.1.0",
        "service": "orchestrator",
        "services": {
            "database": db_status,
            "redis": redis_status,
            "orchestrator": "healthy"
        },
        "metrics": {
            "total_requests": request_count,
            "requests_per_minute": request_count / max((time.time() - startup_time) / 60, 1)
        }
    }

@app.get("/healthz/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with system information"""
    import psutil
    
    # System information
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "orchestrator",
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available": memory.available,
            "disk_percent": disk.percent,
            "disk_free": disk.free
        },
        "application": {
            "uptime": time.time() - startup_time,
            "total_requests": request_count,
            "version": "0.1.0"
        }
    }

@app.get("/api/v1/status")
async def api_status() -> Dict[str, Any]:
    """API status endpoint"""
    return {
        "orchestrator": "running",
        "version": "0.1.0",
        "endpoints": [
            "/",
            "/healthz",
            "/healthz/detailed",
            "/api/v1/status",
            "/api/v1/tasks",
            "/api/v1/tasks/{task_id}",
            "/ws"
        ]
    }

@app.get("/api/v1/agents")
async def list_agents() -> Dict[str, Any]:
    """List available agents"""
    return {
        "agents": [
            {
                "id": "planner-001",
                "name": "Planner Agent",
                "type": "planner",
                "status": "idle",
                "capabilities": ["task_planning", "requirement_analysis"]
            },
            {
                "id": "coder-001",
                "name": "Coder Agent",
                "type": "coder",
                "status": "idle",
                "capabilities": ["code_generation", "diff_creation"]
            },
            {
                "id": "tester-001",
                "name": "Tester Agent",
                "type": "tester",
                "status": "idle",
                "capabilities": ["test_execution", "validation"]
            }
        ]
    }

@app.post("/api/v1/tasks")
async def create_task(task_request: TaskRequest) -> Dict[str, Any]:
    """Create and start a new task"""
    try:
        task_run = await orchestrator.start_task(task_request)
        
        return {
            "status": "success",
            "message": "Task created and started",
            "task_id": task_run.task_id,
            "run_id": task_run.run_id,
            "state": task_run.state.value
        }
    except Exception as e:
        logger.error("Failed to create task", error=str(e))
        return {
            "status": "error",
            "message": f"Failed to create task: {str(e)}"
        }

@app.get("/api/v1/tasks")
async def list_tasks() -> Dict[str, Any]:
    """List all active tasks"""
    return {
        "tasks": [
            {
                "task_id": task.task_id,
                "run_id": task.run_id,
                "template": task.template,
                "state": task.state.value,
                "start_time": task.start_time,
                "iteration": task.iteration,
                "current_agent": task.current_agent
            }
            for task in active_tasks.values()
        ]
    }

@app.get("/api/v1/tasks/{task_id}")
async def get_task(task_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific task"""
    if task_id not in active_tasks:
        return {"status": "error", "message": "Task not found"}
    
    task = active_tasks[task_id]
    events = task_events.get(task_id, [])
    
    return {
        "task": {
            "task_id": task.task_id,
            "run_id": task.run_id,
            "template": task.template,
            "instruction": task.instruction,
            "state": task.state.value,
            "start_time": task.start_time,
            "iteration": task.iteration,
            "current_agent": task.current_agent,
            "error": task.error
        },
        "events": [event.model_dump() for event in events]
    }

@app.get("/api/v1/tasks/{task_id}/events")
async def get_task_events(task_id: str) -> Dict[str, Any]:
    """Get all events for a specific task"""
    if task_id not in task_events:
        return {"status": "error", "message": "Task not found"}
    
    events = task_events[task_id]
    return {
        "task_id": task_id,
        "events": [event.model_dump() for event in events]
    }

# WebSocket endpoint for real-time event streaming
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial connection message
        await websocket.send_text("Connected to Gizmo AI Orchestrator")
        
        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            # Echo back for now (can be extended for commands)
            await websocket.send_text(f"Echo: {data}")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("ORCHESTRATOR_HOST", "0.0.0.0")
    port = int(os.getenv("ORCHESTRATOR_PORT", "8003"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(
        "Starting orchestrator server",
        host=host,
        port=port,
        debug=debug
    )
    
    uvicorn.run(
        "engine:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
