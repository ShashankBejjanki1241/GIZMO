# 🏗️ **Gizmo AI - Project Structure Overview**

## 👨‍💻 **Developer Information**

**Shashank B**  
*Lead Developer & Architect*  
*Last Updated: December 2024*

---

## 📁 **Root Directory Structure**

```
gizmo-ai/
├── 📚 docs/                    # Complete documentation
├── ⚙️ config/                  # Configuration and infrastructure
├── 🧪 tests/                   # Test suites and validation
├── 📜 scripts/                 # Utility and demo scripts
├── 🎨 app/                     # Next.js frontend application
├── 🚀 api/                     # FastAPI backend service
├── 🧠 orchestrator/            # Enhanced orchestration engine
├── 🎯 templates/               # Golden templates for testing
├── 📊 assets/                  # Static assets and diagrams
├── 📋 .cursor/                 # Cursor AI development rules
├── 📖 README.md                # Project overview and quickstart
├── 🎯 PROJECT_INDEX.md         # Complete file index
└── 🚀 Makefile                 # Development automation
```

## 📚 **Documentation (`docs/`)**

### **Requirements (`docs/requirements/`)**
- `PRD.md` - Product Requirements Document (Final)

### **Development (`docs/development/`)**
- `PHASE3_SUMMARY.md` - Secure Execution & Reliable Patching
- `PHASE5_SUMMARY.md` - Real LLM Integration
- `PHASE6_SUMMARY.md` - Realtime "Wow" UI
- `PHASE7_SUMMARY.md` - Reliability & Success Rate Optimization

### **Architecture (`docs/architecture/`)**
- System architecture diagrams
- Component interaction flows
- Security model documentation

### **Deployment (`docs/deployment/`)**
- `deploy.md` - Complete deployment guide
- Service configuration details
- Production setup instructions

### **API (`docs/api/`)**
- API reference documentation
- Endpoint specifications
- Request/response examples

## ⚙️ **Configuration (`config/`)**

### **Docker (`config/docker/`)**
- `docker-compose.yml` - Local development stack
- `Dockerfile.api` - FastAPI service container
- `Dockerfile.ui` - Next.js frontend container
- `Dockerfile.orchestrator` - Orchestration engine container
- `requirements.txt` - Python dependencies

### **Deployment (`config/deployment/`)**
- `vercel.json` - Vercel frontend deployment
- `fly.toml` - Fly.io backend deployment

### **Infrastructure (`config/infra/`)**
- `postgres/` - Database initialization scripts
- `redis/` - Cache configuration
- `nginx/` - Reverse proxy setup (if needed)

## 🧪 **Testing (`tests/`)**

### **Unit Tests (`tests/unit/`)**
- Individual component testing
- Mock and stub implementations

### **Integration Tests (`tests/integration/`)**
- Service interaction testing
- API endpoint validation

### **End-to-End Tests (`tests/e2e/`)**
- `test_orchestrator.py` - Full orchestration flow testing
- `test_real_llm.py` - LLM integration validation
- `test_env_setup.py` - Environment configuration testing

## 📜 **Scripts (`scripts/`)**

### **Demo Scripts**
- `curated_tasks.py` - Phase 7 reliability testing suite
- `demo_phase6.py` - UI features demonstration

### **Utility Scripts**
- Development automation
- Data generation
- Performance testing

## 🎨 **Frontend (`app/`)**

### **Next.js Application**
- `pages/` - Application routes and components
- `components/` - Reusable UI components
- `types/` - TypeScript type definitions
- `styles/` - CSS and styling
- `public/` - Static assets

### **Key Features**
- Real-time WebSocket updates
- Professional showcase task interface
- Download functionality for artifacts
- Replay system for task execution

## 🚀 **Backend (`api/`)**

### **FastAPI Service**
- `main.py` - Application entry point
- `models/` - Data models and schemas
- `routes/` - API endpoint definitions
- `services/` - Business logic implementation
- `middleware/` - Request processing

### **Key Features**
- Health monitoring endpoints
- Structured logging
- Request ID tracking
- CORS configuration

## 🧠 **Orchestrator (`orchestrator/`)**

### **Core Engine**
- `engine.py` - Enhanced orchestration with Phase 7 features
- `protocol.py` - Inter-agent communication models
- `sandbox.py` - Secure execution environment

### **Key Features**
- Multi-agent coordination (Planner → Coder → Tester)
- Memory layer for successful pattern storage
- Auto-retries with graceful fallback
- Failure quarantine system
- Comprehensive metrics tracking

## 🎯 **Templates (`templates/`)**

### **Golden Templates**
- `react/` - React + Jest testing template
- `express/` - Express + Supertest template
- `flask/` - Flask + pytest template

### **Template Features**
- Predictable, known issues
- Failing tests for AI agents to fix
- Pinned dependencies for consistency
- Minimal, focused examples

## 📊 **Assets (`assets/`)**

### **Screenshots**
- UI demonstrations
- Feature showcases
- Performance metrics

### **Diagrams**
- Architecture visualizations
- Component relationships
- Data flow diagrams

## 🔧 **Development Tools**

### **Cursor Rules (`.cursor/`)**
- `rules/main.mdc` - Core development guidelines
- `rules/code-style.mdc` - Code formatting standards
- `rules/testing.mdc` - Testing best practices
- `rules/security.mdc` - Security guidelines
- `rules/pr.mdc` - Pull request standards
- `rules/project-specific.mdc` - Gizmo AI conventions

### **Automation (`Makefile`)**
- `make up` - Start development stack
- `make down` - Stop development stack
- `make logs` - View service logs
- `make rebuild` - Rebuild and restart services
- `make test` - Run test suites

## 🚀 **Deployment Architecture**

### **Production Stack**
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend       │    │   Database      │
│   (Vercel)      │◄──►│   (Fly.io)       │◄──►│   (Supabase)    │
│                 │    │                  │    │                 │
│   - Next.js     │    │   - FastAPI      │    │   - PostgreSQL  │
│   - React       │    │   - Orchestrator │    │   - Real-time   │
│   - WebSocket   │    │   - WebSocket    │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │     Cache       │
                       │   (Upstash)     │
                       │                 │
                       │   - Redis       │
                       │   - Pub/Sub     │
                       └─────────────────┘
```

## 📋 **File Organization Principles**

### **Logical Grouping**
- **Documentation**: All project docs in `docs/` with clear categorization
- **Configuration**: Infrastructure and deployment configs in `config/`
- **Testing**: Complete test coverage organized by type
- **Scripts**: Utility and demo scripts for development and demonstration
- **Source Code**: Clear separation between frontend, backend, and orchestration

### **Professional Standards**
- **Clear Naming**: Descriptive file and directory names
- **Consistent Structure**: Similar projects follow the same organization
- **Easy Navigation**: Logical grouping for quick file location
- **Production Ready**: Shows strong project organization skills

### **Development Workflow**
- **Local Development**: Docker Compose for full-stack development
- **Testing**: Complete test suites for validation
- **Documentation**: Up-to-date docs for all features
- **Deployment**: Production-ready configuration files

---

**🎯 This organized structure shows professional project management, clear documentation, and strong code organization.**
