# SalesFlow Agent - Project Context for AI Assistants

> **Last Updated**: 2026-08-10  
> **Phase**: Story Creation & Implementation  
> **Primary AI**: Walmart Copilot (Opus) | **Secondary AI**: Personal Copilot (Sonnet 4.5)

---

## Quick Start for AI Assistants

**If you're picking up this project for the first time, do this:**

1. Read `HANDOFF-TRACKING.md` in this folder - shows latest status
2. Read this file completely - understand the project
3. Check `_bmad-output/planning-artifacts/` - see PRD, Architecture, Epics
4. Check `_bmad-output/implementation-artifacts/` - see completed stories
5. Start where the handoff log says to start

---

## Project Overview

### Purpose
Demo project for Pinterest GenAI Engineer interview with Peter (hiring manager). Showcases:
- **ReACT Agent Pattern** - LLM reasoning and action execution
- **RAG** - Retrieval Augmented Generation for knowledge search
- **MCP** - Model Context Protocol for tool discovery
- **Workflow Orchestration** - Zeebe/BPMN for process automation

### Success Criteria
- Working demo that executes 3 user journeys (see PRD)
- Clean code following BMad spec-driven development
- Demonstrates all 4 GenAI patterns in one system
- Total cost: $3-5 (using Walmart Opus unlimited + Personal Sonnet for testing)

### Timeline
Interview date: TBD (soon)  
Current: Story creation and initial implementation phase

---

## Technical Architecture

### Stack
- **Language**: Python 3.11+
- **API Framework**: FastAPI
- **LLM Framework**: LangChain 0.3.27, LangGraph
- **LLM Model**: Claude Sonnet 4.5 (via langchain-anthropic)
- **RAG Vector Store**: FAISS
- **MCP Framework**: FastMCP v2.14.0
- **Workflow Engine**: Zeebe (via pyzeebe 4.5.0)
- **Data Store**: SQLite (mock CRM data)
- **Deployment**: Docker Compose (Zeebe), local Python processes

### Components (8 Core)
1. **FastAPI App** - Main entry point, conversation endpoint
2. **LangChain ReACT Agent** - LLM reasoning loop with Claude
3. **FAISS RAG Store** - Embeddings + semantic search
4. **FastMCP Server** - Separate process, SQLite-backed CRM tools
5. **MCP Client** - Dynamic tool discovery and invocation
6. **Zeebe Workflow Engine** - BPMN orchestration (Docker)
7. **pyzeebe Workers** - Lead enrichment + LLM scoring workers
8. **SQLite Database** - Mock CRM data (accounts, contacts, opportunities, objections)

### Data Flows (3 Main)
1. **Pipeline Question Flow**: User → FastAPI → ReACT Agent → MCP Client → FastMCP Server → SQLite → Response
2. **RAG Question Flow**: User → FastAPI → ReACT Agent → FAISS Retriever → Knowledge Base → Response
3. **Lead Qualification Workflow**: User → FastAPI → Zeebe → Enrichment Worker → Scoring Worker → Route Decision

### No-Auth, Single-Tenant, Local-Only
- No authentication (demo only)
- No multi-tenancy
- All components run locally
- Mock data in SQLite

---

## Development Framework: BMad Method

### What is BMad?
Spec-driven development framework with AI-native workflows. Installed via `npx @brainblock/bmad install`.

### BMad Artifacts Created
- **PRD**: `_bmad-output/planning-artifacts/salesflow-agent-prd.md`
- **Architecture**: `_bmad-output/planning-artifacts/salesflow-agent-architecture.md`
- **Epics-Stories**: `_bmad-output/planning-artifacts/salesflow-agent-epics-stories.md`
- **Story Files**: `_bmad-output/implementation-artifacts/*.md` (4 created, 6 remaining)

### BMad Skills Available
- `bmad-create-story` - Generate detailed story spec file
- `bmad-dev-story` - Implement code from story file
- `bmad-quick-dev` - Fast implementation from epics/PRD directly
- `bmad-sprint-planning` - Track epic/story status
- `bmad-code-review` - Adversarial code review

### Story Creation Pattern
```bash
# To create a story file:
# User says: "create story 5" or "create the next story"
# AI invokes: bmad-create-story skill
# Result: Creates _bmad-output/implementation-artifacts/[epic]-[story]-[name].md
```

---

## Work Breakdown

### Epics (5 Total)
1. **Agent Core and Conversational Pipeline** - FastAPI, ReACT, MCP integration
2. **RAG Knowledge Base** - FAISS, embeddings, retriever
3. **MCP CRM Discovery** - FastMCP server, SQLite, tool discovery
4. **Workflow Orchestration** - BPMN, pyzeebe workers, Zeebe
5. **Local Developer Experience** - docker-compose, docs, fixtures

### Stories (10 Total)

#### ✅ Completed Story Files
- **Story 1**: Conversational Pipeline Query (Epic 1)
- **Story 2**: Forecast Question via MCP (Epic 1)
- **Story 3**: Objection Handling Guidance (Epic 2)
- **Story 4**: Discover MCP Tools Dynamically (Epic 3)

#### 🔲 Remaining Story Files (Create These Next)
- **Story 5**: Build Embeddings Index (Epic 2)
- **Story 6**: Workflow Start Endpoint (Epic 4)
- **Story 7**: RAG Enrichment Worker (Epic 4)
- **Story 8**: LLM Scoring Worker (Epic 4)
- **Story 9**: Local Startup Scripts (Epic 5)
- **Story 10**: Demo Fixtures (Epic 5)

### Priority Order
1. Epic 1 + Epic 3 (Agent + MCP) - **Highest Priority**
2. Epic 2 (RAG) - Can run in parallel
3. Epic 4 (Workflow) - After above is working
4. Epic 5 (DevEx) - Final polish

---

## File Structure

```
salesflow-agent/
├── _bmad/                          # BMad framework scripts
├── _bmad-output/
│   ├── planning-artifacts/         # PRD, Architecture, Epics
│   └── implementation-artifacts/   # Story files (4 done, 6 to do)
├── .agents/                        # BMad skills (46 skills, 6 agents)
├── docs/
│   ├── HANDOFF-TRACKING.md         # Walmart ↔ Personal handoff log
│   ├── PROJECT-CONTEXT.md          # This file
│   ├── interview-prep-context.md   # Interview prep details
│   └── sv-resume-latest.pdf        # Satwik's resume
├── salesflow_agent/                # (To be created) - Python package
│   ├── api/                        # FastAPI app
│   ├── agent/                      # LangChain ReACT agent
│   ├── rag/                        # FAISS + embeddings
│   ├── mcp_server/                 # FastMCP server
│   ├── workflows/                  # pyzeebe workers
│   └── data/                       # SQLite + fixtures
├── docker-compose.yml              # (To be created) - Zeebe setup
├── pyproject.toml                  # (To be created) - Python deps
└── README.md                       # (To be created) - Project readme
```

---

## User Journeys (3 Core)

### Journey 1: Pipeline Question
**User**: "What's my pipeline for Q4?"  
**Flow**: ReACT → MCP Client → FastMCP Server (get_pipeline tool) → SQLite → Response  
**Output**: "You have 12 opportunities in Q4 worth $2.4M..."

### Journey 2: Objection Handling
**User**: "How do I handle pricing objections?"  
**Flow**: ReACT → FAISS Retriever → Knowledge Base (objection_handling.md) → Response  
**Output**: "Here are 3 approaches: 1) Value-based pricing..."

### Journey 3: Lead Qualification Workflow
**User**: "Qualify this lead: Acme Corp"  
**Flow**: ReACT → Zeebe (start workflow) → Enrichment Worker (RAG lookup) → Scoring Worker (LLM decision) → Route (Sales/Nurture/Disqualify)  
**Output**: "Lead scored 85/100, routed to Sales. Enrichment: Industry-Software, Size-500..."

---

## Dependencies (Key Packages)

```toml
[project]
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn>=0.32.0",
    "langchain>=0.3.27",
    "langchain-anthropic>=0.3.9",
    "langgraph>=0.2.62",
    "faiss-cpu>=1.9.0",
    "fastmcp>=2.14.0",
    "pyzeebe>=4.5.0",
    "sqlalchemy>=2.0.36",
    "pydantic>=2.10.5",
]
```

---

## Development Workflow

### Walmart Copilot Responsibilities (Opus - Free)
1. **Story Creation**: Use `bmad-create-story` to generate Stories 5-10
2. **Code Implementation**: Use `bmad-quick-dev` or `bmad-dev-story` to write code
3. **Documentation**: Write inline docs, README files
4. **Spec Refinement**: Update architecture or story files as needed

**DO NOT TEST** - VPN blocks external APIs and Docker

### Personal Copilot Responsibilities (Sonnet 4.5 - Paid)
1. **Package Installation**: Run `uv sync`, install dependencies
2. **Testing**: Run FastAPI, test endpoints, validate MCP/RAG/Workflow
3. **Bug Fixes**: Fix errors from test runs
4. **Integration**: Docker compose for Zeebe, wire everything together
5. **Demo Polish**: Final UX, error handling, demo script

### Handoff Protocol
- **Walmart → Personal**: Commit with `[WALMART] description`, update HANDOFF-TRACKING.md with "what needs testing"
- **Personal → Walmart**: Commit with `[PERSONAL] description`, update HANDOFF-TRACKING.md with "test results and next tasks"

---

## Cost Optimization Strategy

### Why This Split Works
- **Story Creation**: Heavy token usage (reading epics, generating detailed specs) → Free Opus
- **Code Generation**: Heavy token usage (implementing features) → Free Opus
- **Testing**: Light token usage (run, see error, fix) → Paid Sonnet
- **Result**: 80%+ of work on free tier, minimal paid usage

### Estimated Token Usage
- Story creation (6 remaining): ~50k tokens → Walmart
- Code implementation (10 stories): ~200k tokens → Walmart
- Testing + fixes (all): ~30k tokens → Personal
- **Total Cost**: ~$1-2 (vs $15-20 if all on personal Sonnet)

---

## Key Context for AI Assistants

### When Creating Stories
- Read the epic definition in `salesflow-agent-epics-stories.md`
- Reference PRD for user journeys and functional requirements
- Reference Architecture for component details
- Follow BMad story template (problem, approach, acceptance criteria, dependencies)
- Save to `_bmad-output/implementation-artifacts/[epic]-[story]-[name].md`

### When Implementing Code
- Use type hints (Python 3.11+ syntax)
- Follow async/await patterns for FastAPI
- Use Pydantic for data models
- Keep functions small and testable
- Add docstrings and inline comments
- Reference architecture for component boundaries

### When Handling Handoffs
- Always pull latest: `git pull origin main`
- Update `HANDOFF-TRACKING.md` with clear notes
- List ALL files changed
- Describe what works, what doesn't, what's next
- Push frequently: `git push origin main`

---

## Common Commands

### Git
```bash
git pull origin main              # Before starting work
git add .
git commit -m "[WALMART] msg"     # Or [PERSONAL]
git push origin main              # After work session
```

### BMad Story Creation
```bash
# AI invokes bmad-create-story skill when user says:
# "create story 5" or "create the next story"
```

### Python (Personal Laptop Only)
```bash
cd ~/Projects/salesflow-agent
uv sync                           # Install dependencies
uv run python -m salesflow_agent  # Run app
```

### Docker (Personal Laptop Only)
```bash
docker-compose up -d              # Start Zeebe
docker-compose down               # Stop Zeebe
```

---

## Questions for AI Assistants

**If you're unsure about something:**
1. Check planning artifacts in `_bmad-output/planning-artifacts/`
2. Check existing story files in `_bmad-output/implementation-artifacts/`
3. Check `HANDOFF-TRACKING.md` for latest status
4. Ask user for clarification

**If you encounter an error:**
- Walmart Copilot: Document it in handoff notes, don't try to test
- Personal Copilot: Try to fix it, document results in handoff notes

---

## Success Metrics

### Definition of Done (Overall Project)
- ✅ All 10 stories implemented
- ✅ All 3 user journeys work end-to-end
- ✅ FastAPI runs without errors
- ✅ MCP server discovers and executes tools
- ✅ FAISS retrieves relevant knowledge
- ✅ Zeebe workflow completes successfully
- ✅ Demo script ready for interview

### Definition of Done (Per Story)
- ✅ Story file created with full context
- ✅ Code implemented following architecture
- ✅ Unit tests pass (if applicable)
- ✅ Integration test works
- ✅ Documented in code comments

---

## Additional Context Files

- **Resume**: `docs/sv-resume-latest.pdf` - Satwik's background
- **Interview Prep**: `docs/interview-prep-context.md` - Interview strategy, Peter's priorities
- **Handoff Log**: `docs/HANDOFF-TRACKING.md` - Real-time work tracking

---

**Remember**: This is a demo project to showcase methodology and patterns to Peter at Pinterest. Keep it simple, focused, and effective. The goal is to demonstrate understanding of ReACT, RAG, MCP, and Workflow orchestration — not to build production-grade software.
