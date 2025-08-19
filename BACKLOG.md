# Gizmo AI - Project Backlog

## 🎯 **Objective**
Lock scope, avoid churn, and make Cursor/AI help you (not fight you).

## 📋 **Backlog Structure**
Three buckets only: **MVP** / **Post-MVP** / **Icebox**

---

## 🚀 **MVP (Minimum Viable Product)**

### **Core Functionality**
- [ ] **Planner Agent**: Generate structured development plans
- [ ] **Coder Agent**: Implement code changes via unified diffs
- [ ] **Tester Agent**: Run tests and validate implementations
- [ ] **Orchestrator**: Coordinate agent workflow and state management
- [ ] **Sandbox**: Secure, network-isolated execution environment
- [ ] **Dashboard**: Real-time monitoring with timeline and diff viewer

### **Showcase Tasks (Demo Requirements)**
- [ ] **React Template**: Add division + divide-by-zero guard
- [ ] **Express Template**: Add `/healthz` endpoint + test
- [ ] **Flask Template**: Add `/sum` endpoint + test

### **Success Criteria (From PRD)**
- [ ] **First event ≤ 5 seconds** after task start
- [ ] **Curated showcase runs pass ≥80%** of the time
- [ ] **Downloadable diffs and logs** for each run
- [ ] **Replay functionality** works without new LLM calls

### **Technical Requirements**
- [ ] **Agent Protocol**: Strict JSON output (no prose)
- [ ] **Sandbox Security**: Network isolation, command allowlist
- [ ] **File Protection**: Patcher validates all operations
- [ ] **Real-time Updates**: WebSocket or SSE for live dashboard

---

## 🔮 **Post-MVP**

### **Enhanced Agents**
- [ ] **Reviewer Agent**: Code review and quality checks
- [ ] **Agent Learning**: Improve based on success/failure patterns
- [ ] **Custom Prompts**: User-configurable agent behaviors

### **Integration & Deployment**
- [ ] **GitHub Integration**: Create PRs, handle webhooks
- [ ] **Authentication**: User roles and permissions
- [ ] **Multi-tenant**: Support multiple projects/teams
- [ ] **Production Deployment**: Scalable infrastructure

### **Advanced Features**
- [ ] **Template Library**: More framework/language support
- [ ] **Custom Tasks**: User-defined task types
- [ ] **Analytics**: Success rates, performance metrics
- [ ] **Collaboration**: Team workflows and sharing

---

## 🧊 **Icebox**

### **Future Possibilities**
- [ ] **Multi-language Support**: Go, Rust, Java, C++
- [ ] **Cloud Integration**: AWS, GCP, Azure templates
- [ ] **Mobile Development**: React Native, Flutter support
- [ ] **Database Operations**: Schema changes, migrations
- [ ] **AI Model Training**: Custom models for specific domains
- [ ] **Enterprise Features**: SSO, audit logs, compliance

---

## 🚫 **Scope Lock Rules**

### **MVP Phase**
- **NO scope changes** without unanimous agreement (you + any reviewer)
- **NO new features** until all MVP items are complete
- **NO template additions** beyond React, Express, Flask
- **Focus**: Make the three showcase tasks work perfectly

### **Post-MVP Phase**
- **Scope changes** require PR review and approval
- **New features** must align with MVP success metrics
- **Template expansion** only after core functionality is stable

### **Icebox Phase**
- **Future planning** only - no implementation until Post-MVP is stable
- **Research and design** allowed, but no development resources

---

## ✅ **Definition of Done**

### **MVP Complete When**
1. All three showcase tasks pass consistently (≥80% success rate)
2. First agent event appears within 5 seconds
3. Diffs and logs are downloadable for each run
4. Replay functionality works without LLM calls
5. Sandbox security is verified (no network access, command allowlist enforced)
6. Dashboard shows real-time progress and artifacts

### **Post-MVP Complete When**
1. MVP is stable and well-tested
2. GitHub integration works end-to-end
3. Authentication and user management implemented
4. Production deployment is stable and monitored

---

## 🔒 **Scope Lock Confirmation**

**Current Status**: MVP scope is **LOCKED** ✅

**Next Gate**: MVP completion with all success criteria met

**Scope Change Process**: 
- Unanimous agreement required (you + reviewer)
- No exceptions for MVP phase
- Document all decisions in this file

---

*This backlog ensures focused development and prevents scope creep while maintaining clear vision for future phases.*
