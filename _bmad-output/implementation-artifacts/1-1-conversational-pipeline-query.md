---
story_id: "1.1"
epic: "Epic 1: Agent Core and Conversational Pipeline"
title: "Conversational pipeline query"
status: "ready-for-dev"
created: 2026-08-09
updated: 2026-08-09
---

# Story 1.1: Conversational pipeline query

## User Story
**As a** demo user  
**I want to** ask the agent "What are my top 5 deals by value?"  
**So that** I can see the highest-value pipeline opportunities

## Business Value
This story delivers the foundational conversational agent capability that demonstrates ReACT reasoning with MCP tool discovery and invocation. It proves the core architecture pattern of natural language → agent reasoning → dynamic tool discovery → CRM data retrieval. This is the first user-facing feature and validates the entire agent/MCP integration stack.

## Acceptance Criteria
```gherkin
Given the FastAPI application is running
And the MCP CRM server is running with seeded deal data
When the user asks "What are my top 5 deals by value?"
Then the agent returns a ranked list of at least 3 deals
And the list includes deal name, amount, and stage for each deal
And the response is produced by calling a discovered MCP CRM tool
And the agent does not hardcode the CRM query logic
```

## Technical Requirements

### Stack & Dependencies
- **Python**: 3.11+
- **LangChain**: Use `langchain-anthropic` for Claude integration
- **Claude API**: Use Claude 3.5 Sonnet or Haiku (cost-effective model)
- **FastAPI**: Latest stable for HTTP endpoints
- **FastMCP**: For the separate MCP server process exposing CRM tools
- **SQLite**: Mock CRM data store with seeded deals
- **Environment**: `.env` file for API keys (ANTHROPIC_API_KEY)

### Architecture Compliance

#### Component Structure
This story implements the **FastAPI Application** and **LangChain ReACT Agent** components from the architecture.

**Critical Architecture Points:**
1. **Single FastAPI Host**: All agent logic runs in one FastAPI process - do NOT create separate services
2. **MCP Discovery Pattern**: Agent must discover tools dynamically from FastMCP metadata - NO hardcoded tool definitions
3. **ReACT Agent**: Use LangChain's ReACT pattern where the agent reasons about which tool to call
4. **Local-Only**: No remote vector stores, no auth, no multi-tenant complexity

#### Data Flow (from Architecture)
```
User Query → FastAPI Endpoint → LangChain ReACT Agent
  → MCP Tool Discovery (FastMCP metadata)
  → Agent selects MCP tool (e.g., list_top_deals)
  → Tool invocation returns SQLite data
  → Agent synthesizes natural language response
  → Return to user
```

### File Structure Requirements

**Expected New Files:**
```
salesflow_agent/
  __init__.py                 # Package marker
  main.py                     # FastAPI app entry point
  agent/
    __init__.py
    react_agent.py           # LangChain ReACT agent setup
    tools.py                 # MCP tool wrapper/registration
  mcp/
    __init__.py
    client.py                # MCP client for tool discovery
    crm_server.py            # FastMCP server (separate process)
  models/
    __init__.py
    schemas.py               # Pydantic models for requests/responses
data/
  crm.db                     # SQLite database with seeded deals
  seed_data.sql              # SQL script to populate deals
.env.example                 # Template for API keys
requirements.txt             # Python dependencies
README.md                    # Startup instructions
```

**Critical Implementation Details:**

#### 1. FastAPI Main Application (`salesflow_agent/main.py`)
```python
# Must expose:
# - POST /agent/query endpoint that accepts natural language text
# - Initializes LangChain agent with MCP tools on startup
# - Returns structured response with answer and metadata
```

#### 2. LangChain ReACT Agent (`salesflow_agent/agent/react_agent.py`)
```python
# Must:
# - Use langchain-anthropic Claude chat model
# - Implement ReACT agent pattern with tool calling
# - Accept dynamically discovered MCP tools
# - Return natural language response with tool invocation trace
```

#### 3. MCP Client (`salesflow_agent/mcp/client.py`)
```python
# Must:
# - Discover available tools from FastMCP server on startup
# - Convert MCP tool metadata to LangChain tool format
# - Handle tool invocation and response marshalling
# - Support dynamic tool registration without code changes
```

#### 4. FastMCP CRM Server (`salesflow_agent/mcp/crm_server.py`)
```python
# Must:
# - Use FastMCP framework to expose tools
# - Connect to SQLite crm.db
# - Expose at minimum: list_top_deals(limit: int) tool
# - Return structured deal data: name, amount, stage
# - Run as separate process (not in FastAPI app)
```

#### 5. SQLite Seed Data (`data/seed_data.sql`)
```sql
# Must include:
# - deals table with: id, name, amount, stage, created_at
# - At least 5 seeded deals with varying amounts
# - Stage values: Prospecting, Qualification, Proposal, Negotiation, Closed Won, Closed Lost
```

### Testing Requirements

**Acceptance Test Scenarios:**
1. **Happy Path**: User asks "What are my top 5 deals by value?" and receives ranked list
2. **Variation Query**: User asks "Show me top deals" and agent handles similar intent
3. **Edge Case**: Only 3 deals in database, agent returns 3 (not error)
4. **Tool Discovery**: Agent logs show MCP tool discovery before first query
5. **No Hardcoding**: Code inspection shows agent uses dynamic tool discovery, not hardcoded queries

**Testing Approach:**
- Manual testing via `curl` or API client (Postman/Insomnia)
- Validate agent response includes deal data from SQLite
- Check agent execution trace shows tool selection and invocation
- Verify FastMCP server runs independently and is discoverable

**Test Data Requirements:**
```sql
-- Minimum 5 deals for testing:
-- Deal 1: "Enterprise Cloud Migration" - $500,000 - Negotiation
-- Deal 2: "SMB Software License" - $25,000 - Qualification  
-- Deal 3: "Mid-Market Integration" - $150,000 - Proposal
-- Deal 4: "Startup Package" - $10,000 - Prospecting
-- Deal 5: "Fortune 500 Expansion" - $1,200,000 - Closed Won
```

### Success Criteria Mapping
This story directly implements:
- **FR-1**: Natural language pipeline query
- **FR-2**: Grounded CRM tool invocation via MCP discovery
- **FR-6**: FastMCP discovery of CRM tools
- **FR-7**: Mock CRM data retrieval
- **SM-1**: Demo completes a natural language CRM query end to end

### Dependencies
- **Upstream**: None (this is the first story)
- **Downstream**: Story 1.2 (Forecast question) will reuse the same agent/MCP infrastructure

### Known Constraints
- **Budget**: Keep LLM calls minimal during development. Use Claude Haiku for dev/testing, can upgrade to Sonnet for demo.
- **Local-Only**: No cloud deployment, no authentication, no production security
- **MCP Pattern**: This is a demo of MCP discovery - keep the FastMCP server simple with 1-2 tools maximum for this story
- **No UI**: This story delivers API endpoints only. A future story may add a conversational UI.

## Implementation Notes for Developer

### Critical Success Factors
1. **MCP Discovery is Non-Negotiable**: Do NOT hardcode CRM queries. The agent must discover tools from FastMCP metadata at runtime.
2. **ReACT Pattern**: The agent must reason about tool selection. Use LangChain's built-in ReACT agent, not a custom loop.
3. **Separate Processes**: FastMCP server runs independently from FastAPI app. Use different ports.
4. **Seeded Data**: SQLite must be populated before first run. Include seed script in data/ directory.

### Recommended Development Sequence
1. **Phase 1: Data Foundation**
   - Create SQLite schema for deals table
   - Write seed_data.sql and populate crm.db
   - Verify data with `sqlite3 data/crm.db "SELECT * FROM deals;"`

2. **Phase 2: MCP Server**
   - Implement FastMCP server with list_top_deals tool
   - Test tool independently with MCP client
   - Confirm tool metadata is discoverable

3. **Phase 3: Agent Core**
   - Set up FastAPI app with /agent/query endpoint
   - Implement LangChain ReACT agent with Claude
   - Integrate MCP client to discover and register tools

4. **Phase 4: Integration Testing**
   - Test end-to-end: user query → agent → MCP tool → SQLite → response
   - Validate response format and data accuracy
   - Check agent reasoning trace

5. **Phase 5: Polish**
   - Add README with startup instructions
   - Create .env.example template
   - Document required environment variables

### Potential Pitfalls to Avoid
- **Hardcoding Tool Calls**: Do NOT call SQLite directly from the agent. Must go through MCP discovery.
- **Wrong Agent Pattern**: Do NOT implement custom tool-calling loop. Use LangChain's ReACT agent.
- **Missing Tool Metadata**: FastMCP tools need proper descriptions for the agent to select them correctly.
- **Port Conflicts**: FastAPI and FastMCP must run on different ports (e.g., 8000 and 8001).
- **API Key Leakage**: Never commit .env file. Use .env.example as template only.

### Example Agent Trace (Expected Output)
```
User: "What are my top 5 deals by value?"

Agent Reasoning:
  Thought: I need to retrieve deal data from the CRM system
  Action: list_top_deals
  Action Input: {"limit": 5}
  
Tool Response:
  [
    {"name": "Fortune 500 Expansion", "amount": 1200000, "stage": "Closed Won"},
    {"name": "Enterprise Cloud Migration", "amount": 500000, "stage": "Negotiation"},
    {"name": "Mid-Market Integration", "amount": 150000, "stage": "Proposal"},
    {"name": "SMB Software License", "amount": 25000, "stage": "Qualification"},
    {"name": "Startup Package", "amount": 10000, "stage": "Prospecting"}
  ]
  
Final Answer:
  "Here are your top 5 deals by value:
   1. Fortune 500 Expansion - $1,200,000 (Closed Won)
   2. Enterprise Cloud Migration - $500,000 (Negotiation)
   3. Mid-Market Integration - $150,000 (Proposal)
   4. SMB Software License - $25,000 (Qualification)
   5. Startup Package - $10,000 (Prospecting)"
```

### Environment Setup
```bash
# Required environment variables (.env):
ANTHROPIC_API_KEY=sk-ant-...
MCP_SERVER_URL=http://localhost:8001
FASTAPI_PORT=8000
SQLITE_DB_PATH=data/crm.db
```

### Startup Commands (for README)
```bash
# Terminal 1: Start MCP CRM Server
python -m salesflow_agent.mcp.crm_server

# Terminal 2: Start FastAPI App
python -m salesflow_agent.main

# Test Query
curl -X POST http://localhost:8000/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are my top 5 deals by value?"}'
```

## Definition of Done
- [ ] SQLite database created with deals table and seeded with 5+ deals
- [ ] FastMCP server exposes list_top_deals tool with proper metadata
- [ ] MCP client discovers tools from FastMCP server on startup
- [ ] LangChain ReACT agent configured with Claude and MCP tools
- [ ] FastAPI endpoint accepts natural language queries
- [ ] Agent successfully calls MCP tool and returns ranked deal list
- [ ] Response includes deal name, amount, and stage
- [ ] No hardcoded CRM queries in agent code
- [ ] README documents startup process
- [ ] .env.example includes all required environment variables
- [ ] Manual testing validates all acceptance criteria

## References
- **PRD Section**: 4.1 Conversational Pipeline Assistant, FR-1, FR-2
- **Architecture Section**: LangChain ReACT Agent, FastMCP CRM Server, MCP Client Integration
- **Success Metric**: SM-1 (Demo completes a natural language CRM query end to end)
- **User Journey**: UJ-1 (Sales rep queries top pipeline deals)

---

**Story Status**: Ready for Development  
**Context Engine Analysis**: Complete  
**Developer Guardrails**: Comprehensive  
**Last Updated**: 2026-08-09
