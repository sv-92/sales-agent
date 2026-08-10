# SalesFlow Agent - Demo Guide for Pinterest Interview

## 🎯 Interview Context
- **Position**: GenAI Engineer at Pinterest
- **Interviewer**: Peter
- **Demo Goal**: Showcase BMad Method + GenAI patterns (ReACT, RAG, MCP, Workflows)
- **Budget**: $3-5 total (currently spent ~$0.50)

## ✅ What's Working (Demo-Ready)

### 1. BMad Method Artifacts
Show the **spec-driven development** process:
- **PRD**: `docs/PRD.md` - Product requirements
- **Architecture**: `docs/ARCHITECTURE.md` - Technical design
- **UX Spec**: `docs/UX-SPEC.md` - Interface design
- **Epic Stories**: `_bmad-output/implementation-artifacts/epics-and-stories.md`
- **10 Story Files**: Individual implementation specs

**Key Point**: "Used BMad Method to go from idea → PRD → Architecture → Stories → Code in structured way"

### 2. MCP Integration (WORKING! 🎉)
The **Model Context Protocol** integration is fully functional:

```bash
# Start the application
uv run python -m salesflow_agent

# Test MCP tool discovery (NO API key needed)
curl http://localhost:8000/tools | python3 -m json.tool
```

**Shows 5 CRM tools dynamically discovered:**
- `list_top_deals` - Top deals by value
- `get_forecast` - Sales forecast by quarter
- `search_accounts` - Account search
- `get_contacts` - Contact lookup
- `get_pipeline_summary` - Pipeline stats

**Key Point**: "MCP server running separately, client discovers tools dynamically - this is the standard for AI tool integration"

### 3. Clean Code Architecture
Navigate through the codebase:
```
salesflow_agent/
├── agent/          # ReACT agent (LangChain + LangGraph)
├── mcp/            # MCP server & client
├── rag/            # RAG setup (embeddings disabled on Intel Mac)
├── workflows/      # Zeebe orchestration (optional)
├── models/         # Pydantic data models
└── data/           # SQLite CRM + seed data
```

**Key Point**: "Separation of concerns - each GenAI pattern isolated, testable, swappable"

### 4. FastAPI Endpoints
Open in browser: `http://localhost:8000/docs`

**Working endpoints:**
- `GET /health` - Health check
- `GET /tools` - List discovered MCP tools
- `POST /agent/query` - Agent queries (needs valid Anthropic key)

## ⚠️ Current Blocker

**Anthropic API Key Issue**: All Claude models return 404 "not_found_error"
- Likely cause: Billing not set up or account pending activation
- Fix: https://console.anthropic.com/settings/billing
- Cost to test: ~$0.05 for demo queries

## 🎤 Demo Script (Without Live LLM)

### Opening (1 min)
"I built SalesFlow Agent as a demo of **how I approach GenAI projects** using the BMad Method - a spec-driven development framework. Let me show you the artifacts first, then the code."

### Part 1: Methodology (2 min)
1. Open `docs/PRD.md`
   - "Started with product requirements - what problem, who's the user, what's the value"
2. Open `docs/ARCHITECTURE.md`
   - "Then technical design - 4 GenAI patterns: ReACT agent, RAG, MCP, Workflows"
3. Open `_bmad-output/implementation-artifacts/story-01-*.md`
   - "Broke into 10 stories with full context - each story has acceptance criteria, tech approach, what to test"

### Part 2: MCP Integration (2 min)
```bash
# Show server starting
uv run python -m salesflow_agent
# Wait for "Application startup complete"

# In another terminal, test:
curl http://localhost:8000/tools | python3 -m json.tool
```

**Narration**: "This shows Model Context Protocol in action. The MCP server exposes 5 CRM tools, the client discovers them dynamically at startup. This is the emerging standard - Anthropic, OpenAI all pushing MCP for tool integration."

### Part 3: Code Architecture (2 min)
Walk through:
1. `salesflow_agent/mcp/crm_server.py` - "FastMCP server with @mcp.tool decorators"
2. `salesflow_agent/mcp/client.py` - "Client discovery logic"
3. `salesflow_agent/agent/react_agent.py` - "LangChain ReACT agent with dynamic tools"

**Key Point**: "Each pattern isolated - could swap LangChain for Haystack, swap MCP for function calling, swap SQLite for Salesforce API"

### Part 4: Cost Optimization (1 min)
"I built this across two environments:
- **Walmart laptop** with unlimited Copilot - generated all code (~300k tokens)
- **Personal laptop** for testing - only $0.50 spent
- Learned to split expensive generation vs cheap testing"

### Closing (1 min)
"The LLM queries are blocked by API key billing, but the **infrastructure works**. What I wanted to show is:
1. **Structured thinking** - BMad Method from idea to code
2. **Clean architecture** - GenAI patterns separated
3. **MCP adoption** - Using emerging standards
4. **Fast delivery** - Full stack in ~4 hours of Copilot time"

## 📊 Demo Metrics

| Component | Status | Demo Value |
|-----------|--------|------------|
| BMad Artifacts | ✅ Complete | Shows methodology |
| MCP Server | ✅ Working | Shows tool integration |
| MCP Client | ✅ Working | Shows dynamic discovery |
| Code Quality | ✅ Clean | Shows architecture |
| LLM Queries | ❌ Blocked | Needs valid API key |
| RAG Search | ❌ Disabled | Intel Mac compatibility |

## 🔧 If You Get API Key Working

### Quick Test Commands
```bash
# Start server
uv run python -m salesflow_agent

# Test pipeline query
curl -X POST http://localhost:8000/agent/query \
  -H "Content-Type: application/json" \
  -d '{"message": "What are my top 5 deals?"}'

# Test forecast query
curl -X POST http://localhost:8000/agent/query \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the Q4 forecast?"}'

# Test account search
curl -X POST http://localhost:8000/agent/query \
  -H "Content-Type: application/json" \
  -d '{"message": "Find technology companies in my accounts"}'
```

Expected: Agent will use ReACT pattern to call appropriate MCP tools and return synthesized answers.

## 💡 Interview Tips

**If Peter asks about specific choices:**
- MCP over function calling: "Standardization - Anthropic's pushing it, better than proprietary function calling"
- LangChain over raw API: "Graph execution, memory management, tool routing built-in"
- BMad Method: "Learned this pattern reduces scope creep, keeps specs and code aligned"

**If Peter asks about production readiness:**
- "This is demo quality - production would need auth, rate limiting, observability, error handling"
- "But the patterns are right - MCP for tools, ReACT for reasoning, RAG for knowledge"

**If Peter asks about the dual-laptop approach:**
- "Cost optimization - free tier for heavy generation, paid tier for testing only"
- "Learned to separate expensive LLM work from cheap validation"

## 🎯 Success Criteria

**Minimum viable demo**: Show methodology artifacts + MCP working
**Ideal demo**: Above + live agent queries with working API key
**Interview win**: Peter sees you think architecturally and deliver fast

---

*Built with: Python 3.12, FastAPI, LangChain, FastMCP, SQLite*
*Total cost: ~$0.50 (under $5 budget)*
*Development time: ~4 hours with Copilot*
