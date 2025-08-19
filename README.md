# Multi-Agent AI Developer

A transparent, safe, and demo-able system for end-to-end AI-assisted development with planning → coding → testing workflow.

## 🎯 Problem Statement

Great coding assistants exist, but end-to-end planning→coding→testing is opaque and unsafe. We want a transparent, safe, demo-able system that showcases the full AI development workflow.

## 👥 Target Users

- **Primary**: Recruiters/engineers evaluating AI development capabilities
- **Secondary**: Curious developers exploring AI-assisted workflows

## 🚀 Use Cases

- **UC1**: Run a curated showcase task end-to-end with no setup
- **UC2**: Enter a custom task for a chosen template repo
- **UC3**: Watch agent timeline, inspect diffs, view test logs
- **UC4**: Replay a past successful run (no new LLM calls)

## 🏗️ Architecture

### Core Components
- **Planner Agent**: Generates structured development plans
- **Coder Agent**: Implements code changes based on plans
- **Tester Agent**: Runs tests and validates implementations
- **Orchestrator**: Coordinates agent workflow and state management
- **Sandbox**: Secure, isolated execution environment
- **Dashboard**: Real-time monitoring and artifact viewing

### Technology Stack
- **Backend**: Python 3.11 with FastAPI
- **Frontend**: TypeScript with Next.js
- **Sandbox**: Docker with network isolation
- **Testing**: Jest (JS), pytest (Python), Supertest (Node)
- **Templates**: React+Jest, Express+Supertest, Flask+pytest

## 📋 MVP Scope

### ✅ In Scope
- Three core agents (Planner, Coder, Tester)
- Secure sandbox with network isolation
- Template repositories for different tech stacks
- Real-time dashboard with timeline and diff viewer
- Downloadable artifacts (diffs and logs)
- Replay functionality for successful runs

### ❌ Out of Scope (Post-MVP)
- Reviewer agent
- GitHub PR integration
- Authentication and role management
- Payment processing

## 🎯 User Stories & Acceptance Criteria

1. **Start Task** → Live updates within 5 seconds
2. **View Changes** → Side-by-side diff viewing
3. **Monitor Tests** → Pass/fail counts with stack traces
4. **Replay Runs** → Deterministic replay without LLM calls
5. **Safety First** → Only allowlisted commands, timeout protection

## 🔒 Security & Constraints

- **Budget**: Free tier services only
- **Security**: No outbound network from sandbox
- **Determinism**: Low temperature, strict output parsing
- **Sandbox**: Network-isolated Docker with resource caps

## 📊 Non-Functional Requirements

- **Performance**: P95 end-to-end showcase < 90 seconds
- **Availability**: 99% uptime during demo week
- **Observability**: Structured logging with unique run IDs

## 🚀 **Quick Start - One Liner Commands**

### **Bring Up the Stack**
```bash
make up
```
This single command:
- Starts PostgreSQL database
- Starts Redis cache
- Starts FastAPI backend
- Starts Next.js frontend
- Starts orchestrator service
- Waits for all services to be healthy
- Verifies connectivity

### **Verify Everything is Working**
```bash
make health
```
Checks health of all services:
- API health endpoint
- UI responsiveness
- Database connectivity
- Redis connectivity
- Orchestrator health

### **Monitor Logs**
```bash
make logs
```
Tail logs from all services with:
- Request IDs for tracking
- Service names in logs
- Structured JSON logging
- Real-time updates

### **Stop Everything**
```bash
make down
```

## 🛠️ **Development Commands**

### **Stack Management**
```bash
make up          # Start everything
make down        # Stop everything
make restart     # Restart all services
make build       # Build Docker images
```

### **Monitoring & Debugging**
```bash
make health      # Check all service health
make logs        # Tail all logs
make logs-api    # Tail API logs only
make logs-ui     # Tail UI logs only
make logs-orch   # Tail orchestrator logs only
```

### **Testing**
```bash
make test        # Run all tests
make test-api    # Run API tests only
make test-ui     # Run UI tests only
```

### **Database Operations**
```bash
make db-shell    # Open PostgreSQL shell
make db-backup   # Create database backup
make db-reset    # Reset database (WARNING: destroys data)
```

### **Cleanup**
```bash
make clean       # Remove all containers, volumes, images
```

## 📁 **Project Structure**

```
Gizmo/
├── README.md                     # This file
├── BACKLOG.md                    # Project backlog (MVP/Post-MVP/Icebox)
├── SHOWCASE_TASKS.md             # Three showcase task definitions
├── SCOPE_LOCK_AGREEMENT.md       # MVP scope lock agreement
├── SCOPE_SUMMARY.md              # Quick scope reference
├── PROJECT_INDEX.md              # Complete project structure
├── FILE_STATUS_INDEX.md          # File status tracker
├── Makefile                      # Development commands
├── docker-compose.yml            # Local development stack
├── requirements.txt              # Python dependencies
├── .cursor/                      # Cursor rules and configuration
├── app/                          # Next.js frontend
├── api/                          # FastAPI backend
├── orchestrator/                 # Core orchestration engine
├── templates/                    # Template repositories
├── infra/                        # Infrastructure setup
├── docs/                         # Documentation
└── tests/                        # Test suites
```

## 🔧 **Prerequisites**

- **Docker**: Latest version with Docker Compose
- **Make**: Available on most Unix-like systems
- **curl**: For health checks
- **jq**: For JSON parsing (optional, for prettier output)

## 📚 **Documentation**

- [API Reference](./docs/api.md)
- [Agent Protocols](./docs/agents.md)
- [Sandbox Security](./docs/security.md)
- [Dashboard Guide](./docs/dashboard.md)
- [Contributing Guidelines](./CONTRIBUTING.md)

## 🤝 **Contributing**

We welcome contributions! Please see our [Contributing Guidelines](./CONTRIBUTING.md) for details on:

- Code of Conduct
- Development Setup
- Pull Request Process
- Testing Requirements
- Security Considerations

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## 🙏 **Acknowledgments**

- Inspired by modern AI coding assistants
- Built with security and transparency in mind
- Designed for educational and demonstration purposes

---

**Status**: 🚧 In Development (MVP Phase)

*Building the future of transparent AI-assisted development, one agent at a time.*
