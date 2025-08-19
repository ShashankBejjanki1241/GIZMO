"""
Multi-Agent AI Developer - FastAPI Backend
Main application entry point with health endpoints and logging
"""

import os
import uuid
import time
from contextlib import asynccontextmanager
from typing import Dict, Any

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Multi-Agent AI Developer API", version="0.1.0")
    yield
    # Shutdown
    logger.info("Shutting down Multi-Agent AI Developer API")

# Create FastAPI application
app = FastAPI(
    title="Multi-Agent AI Developer API",
    description="Backend API for the Multi-Agent AI Developer system",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
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
        "Request started",
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
        "Request completed",
        request_id=request_id,
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        duration=duration,
        request_number=request_count
    )
    
    return response

@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint"""
    return {
        "message": "Multi-Agent AI Developer API",
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
        "services": {
            "database": db_status,
            "redis": redis_status,
            "api": "healthy"
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
        "api": "running",
        "version": "0.1.0",
        "endpoints": [
            "/",
            "/healthz",
            "/healthz/detailed",
            "/api/v1/status"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(
        "Starting API server",
        host=host,
        port=port,
        debug=debug
    )
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
