# Gizmo Project - Complete Cursor Rules Overview

## 🎯 What This Is
A comprehensive, organized set of Cursor rules that guide AI assistance and code generation for the Gizmo project. These rules ensure consistency, quality, and best practices across all development work.

## 📁 Complete File Structure

```
Gizmo/
├── CURSOR_RULES_OVERVIEW.md    # This file - complete overview
├── .cursor/
│   ├── index.mdc               # Main entry point and rule index
│   ├── README.md               # Usage documentation
│   └── rules/
│       ├── main.mdc            # Core project rules
│       ├── code-style.mdc      # Code formatting standards
│       ├── testing.mdc         # Testing guidelines
│       ├── security.mdc        # Security best practices
│       ├── pr.mdc              # PR and review guidelines
│       └── project-specific.mdc # Gizmo AI rules
```

## 🔧 How It Works

### Rule Application
- **`index.mdc`**: Main entry point, always applied to all files
- **`main.mdc`**: Core project rules, always applied
- **`code-style.mdc`**: Applied to source code files
- **`testing.mdc`**: Applied to test files and source code
- **`security.mdc`**: Applied to all files for security awareness
- **`pr.mdc`**: Guidelines for pull requests and code reviews
- **`project-specific.mdc`**: Gizmo AI project conventions

### File Patterns (Globs)
- **`**/*`**: All files (for main rules)
- **`**/*.{js,ts,jsx,tsx,py,java,cpp,c,go,rs}`**: Source code files
- **`**/*.test.{js,ts,jsx,tsx,py,java,cpp,c,go,rs}`**: Test files
- **`**/*.spec.{js,ts,jsx,tsx,py,java,cpp,c,go,rs}`**: Spec files

## 📋 Rule Categories & Coverage

### 1. **Core Development** (`main.mdc`)
- ✅ Project overview and guidelines
- ✅ Code style and quality standards
- ✅ File organization principles
- ✅ Documentation requirements
- ✅ Testing strategies
- ✅ Security practices
- ✅ Performance considerations
- ✅ Git and version control
- ✅ AI assistance guidelines
- ✅ Technology stack decisions
- ✅ Code review processes
- ✅ Communication standards

### 2. **Code Style** (`code-style.mdc`)
- ✅ General formatting rules
- ✅ JavaScript/TypeScript standards
- ✅ Python conventions (PEP 8)
- ✅ Comment guidelines
- ✅ Error handling patterns
- ✅ Function size limits
- ✅ Naming conventions

### 3. **Testing** (`testing.mdc`)
- ✅ Test structure and organization
- ✅ Test quality standards
- ✅ Coverage requirements (80%+)
- ✅ Test data management
- ✅ Assertion best practices
- ✅ Deterministic testing
- ✅ Mock and fixture usage

### 4. **Security** (`security.mdc`)
- ✅ Authentication & authorization
- ✅ Input validation
- ✅ Data protection
- ✅ Code security
- ✅ Network security
- ✅ Environment variable usage
- ✅ Security logging

### 5. **Pull Requests** (`pr.mdc`)
- ✅ Conventional commit format
- ✅ PR body structure
- ✅ Review checklist
- ✅ Mermaid diagram usage
- ✅ Testing requirements
- ✅ Documentation updates

### 6. **Gizmo AI** (`project-specific.mdc`)
- ✅ Project architecture and components
- ✅ Agent protocol contracts (Planner, Coder, Tester)
- ✅ Sandbox security requirements
- ✅ Development conventions (Python 3.11, TypeScript/Next.js)
- ✅ Testing and validation standards
- ✅ File layout and structure
- ✅ Security constraints and allowlists

## 🚀 Benefits of This Structure

### **For Developers**
- Clear, consistent coding standards
- Automated quality checks
- Best practices always applied
- Easy to find specific guidelines
- Project-specific conventions clearly defined

### **For AI Assistance**
- Consistent code generation
- Quality-focused suggestions
- Security-aware recommendations
- Testing-first approach
- Project architecture understanding

### **For Project Maintenance**
- Organized rule management
- Easy to update and extend
- Clear documentation
- Scalable structure
- Project-specific requirements documented

## 🔄 How to Use

### **Daily Development**
1. Rules are automatically applied when working with AI
2. Follow the guidelines for consistent code
3. Use the index to find specific rules
4. Reference project-specific rules for architecture decisions

### **Adding New Rules**
1. Create new `.mdc` file in `.cursor/rules/`
2. Add proper frontmatter
3. Update `index.mdc`
4. Follow established format

### **Updating Existing Rules**
1. Edit the specific rule file
2. Test the changes
3. Update documentation if needed
4. Ensure consistency across files

## 📚 Documentation Files

- **`CURSOR_RULES_OVERVIEW.md`**: This comprehensive overview
- **`.cursor/README.md`**: Technical usage guide
- **`.cursor/index.mdc`**: Rule index and quick reference
- **Individual rule files**: Detailed guidelines for specific areas

## 🎯 Key Principles

1. **Consistency**: All rules follow the same format and structure
2. **Completeness**: Cover all major development areas
3. **Maintainability**: Easy to update and extend
4. **Usability**: Clear, actionable guidelines
5. **Integration**: Works seamlessly with Cursor AI
6. **Project-Specific**: Tailored to Multi-Agent AI Developer needs

## 🔍 Quick Start

1. **View Rules**: Check `.cursor/index.mdc` for quick reference
2. **Find Specific Rules**: Use the categorized structure
3. **Follow Guidelines**: Apply rules in your daily development
4. **Extend Rules**: Add new rules as your project grows
5. **Project Rules**: Reference `project-specific.mdc` for architecture decisions

---

*This structure ensures your Gizmo project maintains high code quality, consistency, and follows industry best practices through AI-assisted development, with specific focus on the Gizmo AI project requirements.*
