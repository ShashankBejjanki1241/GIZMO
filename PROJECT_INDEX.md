# Gizmo AI - Complete Project Index

## 🎯 Project Overview
This document provides a complete index of all files in the Gizmo AI project, organized by their purpose and relationship to Cursor rules.

## 📁 Complete File Structure

```
Gizmo/
├── PROJECT_INDEX.md              # This file - complete project index
├── FILE_STATUS_INDEX.md          # File status and next steps
├── BACKLOG.md                    # Project backlog (MVP/Post-MVP/Icebox)
├── SHOWCASE_TASKS.md             # Three showcase task definitions
├── SCOPE_LOCK_AGREEMENT.md       # MVP scope lock agreement
├── README.md                     # Main project documentation
├── CURSOR_RULES_OVERVIEW.md      # Cursor rules overview
├── .cursor/                      # Cursor rules and configuration
│   ├── index.mdc                 # Main rules index
│   ├── README.md                 # Rules usage guide
│   └── rules/
│       ├── main.mdc              # Core development rules
│       ├── code-style.mdc        # Code formatting standards
│       ├── testing.mdc           # Testing guidelines
│       ├── security.mdc          # Security best practices
│       ├── pr.mdc                # PR and review guidelines
│       └── project-specific.mdc  # Gizmo AI rules
├── app/                          # Next.js frontend application
│   └── README.md                 # Frontend documentation
├── api/                          # FastAPI backend
│   └── main.py                   # API entry point
├── orchestrator/                 # Core orchestration engine
│   ├── engine.py                 # Main orchestration logic
│   ├── patcher.py                # File operation validation
│   ├── protocol.py               # Agent communication protocols
│   ├── sandbox.py                # Sandbox management
│   └── prompts/                  # Versioned agent prompts
│       ├── planner.md            # Planner agent prompts
│       ├── coder.md              # Coder agent prompts
│       └── tester.md             # Tester agent prompts
├── docs/                         # Project documentation
│   └── PRD.md                    # Product Requirements Document
├── infra/                        # Infrastructure and deployment
└── tests/                        # Test suites
```

## 🔗 File-to-Rules Mapping

### 📚 **Documentation & Indexes**
| File | Purpose | Related Cursor Rules |
|------|---------|---------------------|
| `README.md` | Main project documentation | `main.mdc`, `project-specific.mdc` |
| `CURSOR_RULES_OVERVIEW.md` | Cursor rules overview | All rule files |
| `PROJECT_INDEX.md` | Complete project index | All rule files |
| `FILE_STATUS_INDEX.md` | File status tracker | All rule files |
| `BACKLOG.md` | Project backlog and scope | `project-specific.mdc` |
| `SHOWCASE_TASKS.md` | Showcase task definitions | `project-specific.mdc` |
| `SCOPE_LOCK_AGREEMENT.md` | MVP scope lock | `project-specific.mdc` |

### 🎮 **Cursor Rules & Configuration**
| File | Purpose | Applies To |
|------|---------|------------|
| `.cursor/index.mdc` | Main rules index | All files |
| `.cursor/README.md` | Rules usage guide | All files |
| `.cursor/rules/main.mdc` | Core development rules | All files |
| `.cursor/rules/code-style.mdc` | Code formatting standards | Source code files |
| `.cursor/rules/testing.mdc` | Testing guidelines | Test files + source code |
| `.cursor/rules/security.mdc` | Security best practices | All files |
| `.cursor/rules/pr.mdc` | Pull request guidelines | All files |
| `.cursor/rules/project-specific.mdc` | Gizmo AI rules | All files |

### 🖥️ **Frontend Application (Next.js)**
| File | Purpose | Related Rules |
|------|---------|---------------|
| `app/README.md` | Frontend documentation | `code-style.mdc`, `project-specific.mdc` |
| *Future files* | React components, pages, styles | `code-style.mdc`, `testing.mdc` |

### 🔧 **Backend API (FastAPI)**
| File | Purpose | Related Rules |
|------|---------|---------------|
| `api/main.py` | API entry point | `code-style.mdc`, `security.mdc`, `project-specific.mdc` |
| *Future files* | API endpoints, models, schemas | `code-style.mdc`, `testing.mdc`, `security.mdc` |

### 🧠 **Orchestrator Engine**
| File | Purpose | Related Rules |
|------|---------|---------------|
| `orchestrator/engine.py` | Main orchestration logic | `code-style.mdc`, `testing.mdc`, `project-specific.mdc` |
| `orchestrator/patcher.py` | File operation validation | `security.mdc`, `project-specific.mdc` |
| `orchestrator/protocol.py` | Agent communication protocols | `code-style.mdc`, `testing.mdc`, `project-specific.mdc` |
| `orchestrator/sandbox.py` | Sandbox management | `security.mdc`, `project-specific.mdc` |

### 💬 **Agent Prompts**
| File | Purpose | Related Rules |
|------|---------|---------------|
| `orchestrator/prompts/planner.md` | Planner agent prompts | `project-specific.mdc` |
| `orchestrator/prompts/coder.md` | Coder agent prompts | `project-specific.mdc` |
| `orchestrator/prompts/tester.md` | Tester agent prompts | `project-specific.mdc` |

### 🧪 **Test Suites**
| Directory | Purpose | Related Rules |
|------------|---------|---------------|
| `tests/` | All test files | `testing.mdc`, `project-specific.mdc` |

### 🏗️ **Infrastructure**
| Directory | Purpose | Related Rules |
|------------|---------|---------------|
| `infra/` | Deployment and infrastructure | `project-specific.mdc` |

## 🎯 **Rule Application Matrix**

### **Always Applied Rules**
- `.cursor/rules/main.mdc` - Core development guidelines
- `.cursor/rules/security.mdc` - Security best practices
- `.cursor/rules/project-specific.mdc` - Project conventions

### **Conditionally Applied Rules**
- `.cursor/rules/code-style.mdc` - Applied to source code files
- `.cursor/rules/testing.mdc` - Applied to test files and source code
- `.cursor/rules/pr.mdc` - Applied during pull request creation

### **File Type Specific Rules**
- **Python files** (`.py`): `code-style.mdc`, `testing.mdc`, `security.mdc`
- **TypeScript files** (`.ts`, `.tsx`): `code-style.mdc`, `testing.mdc`, `security.mdc`
- **JavaScript files** (`.js`, `.jsx`): `code-style.mdc`, `testing.mdc`, `security.mdc`
- **Markdown files** (`.md`): `main.mdc`, `project-specific.mdc`
- **Cursor rules** (`.mdc`): `main.mdc`, `project-specific.mdc`

## 🔍 **Quick Navigation**

### **For Developers**
- **Start Here**: `README.md` → `PROJECT_INDEX.md` → Specific files
- **Scope Control**: `BACKLOG.md` → `SCOPE_LOCK_AGREEMENT.md`
- **Showcase Tasks**: `SHOWCASE_TASKS.md` → Task definitions
- **Rules Reference**: `.cursor/index.mdc` → Specific rule files

### **For AI Assistance**
- **Core Rules**: `.cursor/rules/main.mdc` + `.cursor/rules/project-specific.mdc`
- **Code Quality**: `.cursor/rules/code-style.mdc` + `.cursor/rules/testing.mdc`
- **Security**: `.cursor/rules/security.mdc` + `.cursor/rules/project-specific.mdc`

### **For Project Management**
- **Architecture**: `docs/PRD.md` + `orchestrator/` files
- **Development**: `app/` + `api/` + `orchestrator/` directories
- **Testing**: `tests/` directory + testing rules
- **Scope Control**: `BACKLOG.md` + `SCOPE_LOCK_AGREEMENT.md`

## 📊 **File Statistics**

- **Total Files**: 23 files
- **Cursor Rules**: 7 rule files
- **Documentation**: 7 documentation files
- **Source Code**: 4 Python files
- **Agent Prompts**: 3 prompt files
- **Configuration**: 2 configuration files

## 🚀 **Next Steps**

1. **Review Rules**: Check `.cursor/index.mdc` for complete rule overview
2. **Understand Scope**: Read `BACKLOG.md` and `SCOPE_LOCK_AGREEMENT.md`
3. **Review Tasks**: Check `SHOWCASE_TASKS.md` for demo requirements
4. **Explore Structure**: Navigate through organized directories
5. **Follow Guidelines**: Apply Cursor rules in daily development
6. **Extend Project**: Add new files following established structure

---

*This index ensures complete visibility into your Gizmo AI project structure and how it integrates with Cursor rules for consistent, high-quality development.*
