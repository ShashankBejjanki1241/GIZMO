# 🚀 **Gizmo AI - Multi-Agent AI Developer Platform**

> **Transparent, safe, and demo-able AI-powered software development with real-time visibility into the planning→coding→testing loop.**


## 👨‍💻 **Developer**

**Shashank B**  
*Lead Developer & Architect*  
*Last Updated: Aug 2025*

---

## 🎯 **Quick Start**

```bash
# Clone and setup
git clone https://github.com/ShashankBejjanki1241/GIZMO.git
cd GIZMO

# Install dependencies
npm install
pip install -r requirements.txt

# Start development stack
docker-compose up -d
npm run dev
```

## 🚀 **Live Demo**

Experience Gizmo AI in action: [Demo Link Coming Soon]

---

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend       │    │   Database      │
│   (Next.js)     │◄──►│   (FastAPI)      │◄──►│   (PostgreSQL)  │
│                 │    │                  │    │                 │
│   - React       │    │   - Orchestrator │    │   - Real-time   │
│   - WebSocket   │    │   - WebSocket    │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │     Cache       │
                       │   (Redis)       │
                       │                 │
                       │   - Pub/Sub     │
                       └─────────────────┘
```

## 🛠️ **Technology Stack**

### **Frontend**
- **Framework**: Next.js 14 with TypeScript
- **UI Library**: React 18 with Tailwind CSS
- **State Management**: React Hooks + Context
- **Real-time**: WebSocket integration

### **Backend**
- **API Framework**: FastAPI (Python 3.11)
- **Orchestration**: Custom AI agent orchestrator
- **Authentication**: JWT-based (planned)
- **Validation**: Pydantic models

### **Infrastructure**
- **Database**: PostgreSQL 15
- **Caching**: Redis 7
- **Containerization**: Docker & Docker Compose
- **AI Integration**: OpenAI GPT-4o-mini

### **Development Tools**
- **Package Manager**: npm (Node.js), pip (Python)
- **Testing**: Jest, pytest
- **Linting**: ESLint, Prettier, Black
- **Version Control**: Git

## 🚀 **Features**

- **Multi-Agent Workflow**: Planner → Coder → Tester
- **Real-time Updates**: WebSocket integration
- **Secure Sandbox**: Network isolation and resource limits
- **Memory Layer**: Learning from successful patterns
- **Auto-retries**: Graceful error handling
- **Professional UI**: Status tracking and artifact downloads

## 📁 **Project Structure**

The project follows a clean, modular architecture. For detailed information, see:
- [Project Index](PROJECT_INDEX.md) - Comprehensive file mapping and organization
- [Project Structure](PROJECT_STRUCTURE.md) - Detailed directory layout and architecture

```
gizmo-ai/
├── app/                    # Next.js frontend
├── api/                    # FastAPI backend
├── orchestrator/           # AI orchestration engine
├── templates/              # Testing templates
└── requirements.txt        # Python dependencies
```

## 🔧 **Development**

```bash
# Install dependencies
npm install
pip install -r requirements.txt

# Run tests
npm test
python -m pytest

# Start development
npm run dev
```

## 📄 **License**

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

**🚀 Ready to revolutionize AI-assisted development!**
