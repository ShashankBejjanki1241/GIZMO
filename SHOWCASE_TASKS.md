# Gizmo AI - Showcase Tasks

## 🎯 **Objective**
Define the three showcase tasks that will demonstrate the Gizmo AI system end-to-end.

## 🚀 **Showcase Task 1: React Template**

### **Task Description**
Add division functionality with divide-by-zero guard to a React calculator component.

### **Starting State**
```jsx
// Basic React calculator with addition, subtraction, multiplication
function Calculator() {
  const [result, setResult] = useState(0);
  const [input1, setInput1] = useState('');
  const [input2, setInput2] = useState('');
  
  const add = () => setResult(Number(input1) + Number(input2));
  const subtract = () => setResult(Number(input1) - Number(input2));
  const multiply = () => setResult(Number(input1) * Number(input2));
  
  // Missing: division functionality
}
```

### **Expected Changes**
1. **Add division function** with proper error handling
2. **Implement divide-by-zero guard** with user-friendly error message
3. **Add division button** to the UI
4. **Update tests** to cover new functionality

### **Success Criteria**
- [ ] Division operation works correctly
- [ ] Divide-by-zero shows error message (not crash)
- [ ] UI includes division button
- [ ] Tests pass for new functionality
- [ ] Code follows React best practices

---

## 🚀 **Showcase Task 2: Express Template**

### **Task Description**
Add a `/healthz` health check endpoint with comprehensive testing.

### **Starting State**
```javascript
// Basic Express server with minimal endpoints
const express = require('express');
const app = express();

app.get('/', (req, res) => {
  res.json({ message: 'Hello World' });
});

// Missing: health check endpoint
```

### **Expected Changes**
1. **Add `/healthz` endpoint** that returns health status
2. **Include system metrics** (uptime, memory usage, etc.)
3. **Add comprehensive tests** using Supertest
4. **Handle edge cases** and error scenarios

### **Success Criteria**
- [ ] `/healthz` endpoint responds with health status
- [ ] Returns JSON with system information
- [ ] Tests cover endpoint functionality
- [ ] Tests cover error scenarios
- [ ] All tests pass

---

## 🚀 **Showcase Task 3: Flask Template**

### **Task Description**
Add a `/sum` endpoint that calculates the sum of provided numbers with proper testing.

### **Starting State**
```python
# Basic Flask app with minimal endpoints
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({'message': 'Hello World'})

# Missing: sum endpoint
```

### **Expected Changes**
1. **Add `/sum` endpoint** that accepts numbers
2. **Handle query parameters** for number input
3. **Implement input validation** for numbers
4. **Add comprehensive tests** using pytest
5. **Handle edge cases** (no numbers, invalid input)

### **Success Criteria**
- [ ] `/sum` endpoint calculates sum correctly
- [ ] Handles query parameters properly
- [ ] Validates input and handles errors
- [ ] Tests cover all scenarios
- [ ] All tests pass

---

## 🎯 **Showcase Success Metrics**

### **Performance Requirements**
- **First agent event**: ≤ 5 seconds after task start
- **End-to-end completion**: P95 < 90 seconds
- **Success rate**: ≥80% on curated showcase tasks

### **Quality Requirements**
- **Code quality**: Follows language-specific best practices
- **Test coverage**: All new functionality tested
- **Error handling**: Graceful handling of edge cases
- **Documentation**: Clear code comments and structure

### **Security Requirements**
- **Sandbox isolation**: No network access
- **Command allowlist**: Only permitted commands executed
- **File protection**: Critical files cannot be modified
- **Input validation**: All user inputs validated

---

## 🔄 **Showcase Workflow**

### **1. Task Initiation**
- User selects showcase task from dashboard
- System creates isolated sandbox environment
- Task description and starting code provided

### **2. Agent Execution**
- **Planner**: Generates structured development plan
- **Coder**: Implements changes via unified diffs
- **Tester**: Runs tests and validates implementation

### **3. Result Delivery**
- **Real-time updates** via dashboard
- **Downloadable diffs** for code changes
- **Downloadable logs** for execution history
- **Replay capability** for successful runs

---

## 📊 **Showcase Validation**

### **Automated Checks**
- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] Security constraints enforced
- [ ] Performance targets met

### **Manual Verification**
- [ ] Functionality works as expected
- [ ] UI/UX is intuitive
- [ ] Error handling is user-friendly
- [ ] Code is maintainable

---

## 🚫 **Scope Constraints**

### **MVP Limitations**
- **No additional features** beyond the three showcase tasks
- **No framework changes** - use existing templates
- **No performance optimizations** beyond basic requirements
- **Focus**: Make these three tasks work perfectly

### **Success Definition**
Showcase tasks are successful when:
1. All three tasks complete within time limits
2. Success rate ≥80% on repeated runs
3. Diffs and logs are downloadable
4. Replay functionality works
5. Sandbox security is maintained

---

*These showcase tasks provide a focused, achievable demonstration of the Gizmo AI system while maintaining strict scope control.*
