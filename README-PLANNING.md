# Planning Documentation for Agent Cube

Agent Cube is a **framework** - it provides structure and process, but **you bring the planning docs**.

## What Agent Cube Provides

✅ **Templates** - What planning documents to create  
✅ **Structure** - How to organize phases, agents, tasks  
✅ **Process** - Dual-writer workflow, judge panels, synthesis  
✅ **Automation** - CLI tools to orchestrate the workflow  

## What You Provide

📋 **Your Planning Documents** - The actual requirements for your project:

### Recommended Planning Structure

Create a `planning/` directory with documents for:

**Core Architecture:**
- `architecture.md` - Services, boundaries, diagrams, invariants
- `api-conventions.md` - Versioning, envelopes, errors, headers, pagination
- `error-handling.md` - Error taxonomy, envelopes, mapping rules
- `monorepo-architecture.md` - Workspace structure, package conventions

**Development:**
- `developer-workflow.md` - Dev setup, branching, PRs
- `code-quality.md` - ESLint, prettier, testing standards
- `ci-cd.md` - Pipeline stages, preview environments

**Data & Backend:**
- `db-conventions.md` - Schema naming, IDs, soft-deletes
- `migrations.md` - Migration strategy, reversibility
- `observability.md` - Logging, tracing, metrics

**Security:**
- `security-compliance.md` - Auth, RBAC, auditing
- `secrets-config.md` - Secret management, no .env files

**And more as needed...**

### Example Planning Doc

```markdown
# API Conventions

## Error Envelope

All errors return:
```json
{
  "error": {
    "code": "validation_error",
    "message": "One or more fields failed validation",
    "requestId": "req_123"
  }
}
```

## Headers

- `API-Version`: YYYY-MM-DD format
- `Request-ID`: Correlation ID for tracing
...
```

## How Agents Use Your Planning Docs

1. **Orchestrator** reads your planning docs
2. **Creates task prompts** that reference specific planning docs
3. **Writers** implement according to YOUR requirements
4. **Judges** verify against YOUR planning docs
5. **Synthesis** ensures final solution matches YOUR standards

## Getting Started

1. **Create your planning directory**:
   ```bash
   mkdir -p planning
   ```

2. **Write your first planning doc**:
   ```bash
   # Example: API error handling
   cat > planning/error-handling.md << 'EOF'
   # Error Handling
   
   All API errors must return:
   - HTTP status code
   - Error envelope with code, message, requestId
   - No stack traces in production
   EOF
   ```

3. **Reference it in task prompts**:
   ```bash
   # In your writer prompt
   Planning Docs (Golden Source):
   - planning/error-handling.md
   ```

4. **Agents will follow it!** They read your planning docs and implement exactly what you specified.

## Best Practices

✅ **Be specific** - The more detailed your planning docs, the better agent output  
✅ **Use examples** - Show good/bad code patterns  
✅ **Reference liberally** - Link planning docs in task prompts  
✅ **Keep updated** - Treat planning docs as living documentation  
❌ **Don't skip planning** - Agents need clear requirements  

## See Also

- `AGENT_CUBE.md` - Complete framework guide
- Lines 190-210 - Planning foundation section
- Lines 225-253 - Phase & task derivation from planning docs

