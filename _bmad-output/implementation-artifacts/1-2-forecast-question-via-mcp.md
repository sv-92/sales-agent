---
story_id: "1.2"
epic: "Epic 1: Agent Core and Conversational Pipeline"
title: "Forecast question via MCP"
status: "ready-for-dev"
created: 2026-08-09
updated: 2026-08-09
---

# Story 1.2: Forecast question via MCP

## User Story
**As a** demo user  
**I want to** ask "What's the forecast for Q3?"  
**So that** I can see sales projection data from the mock CRM

## Business Value
This story extends the MCP tool discovery pattern to include forecast data, demonstrating that the agent can handle multiple CRM data types without code changes. It validates the extensibility promise of MCP: adding a new data source (forecasts) requires only defining a new tool in the FastMCP server, not modifying the agent. This proves the architecture's flexibility for real-world CRM expansion scenarios.

## Acceptance Criteria
```gherkin
Given the FastAPI application is running
And the MCP CRM server exposes a forecast tool
And the forecast database contains Q3 data
When the user asks "What's the forecast for Q3?"
Then the agent calls the MCP forecast tool
And the answer includes a forecast number or summary for Q3
And the response is natural language with financial data formatted appropriately
And the agent discovers the forecast tool dynamically (no hardcoded forecast logic)
```

## Technical Requirements

### Stack & Dependencies
- **Python**: 3.11+ (same as Story 1.1)
- **LangChain**: Reuse existing `langchain-anthropic` setup from Story 1.1
- **Claude API**: Continue using Claude 3.5 Sonnet or Haiku
- **FastAPI**: Existing FastAPI app from Story 1.1
- **FastMCP**: Extend existing MCP server with new forecast tool
- **SQLite**: Add forecasts table to existing `crm.db`
- **Environment**: Same `.env` file from Story 1.1 (no new keys needed)

### Architecture Compliance

#### Component Structure
This story extends components already established in Story 1.1:
- **FastAPI Application**: No changes needed - same `/agent/query` endpoint
- **LangChain ReACT Agent**: No changes - agent already supports dynamic tool discovery
- **FastMCP CRM Server**: **UPDATE** - add new `get_forecast` tool alongside existing `list_top_deals`
- **SQLite CRM Database**: **UPDATE** - add forecasts table with seeded quarterly data

**Critical Architecture Points:**
1. **Zero Agent Changes**: The agent code should NOT be modified. Tool discovery handles new forecast tool automatically.
2. **MCP Extensibility Pattern**: Adding forecast support only requires FastMCP server changes and database schema updates.
3. **Same Data Flow**: Query → Agent → MCP Discovery → Tool Selection → SQLite → Response (same as Story 1.1).

#### Data Flow (from Architecture)
```
User Query: "What's the forecast for Q3?" 
  → FastAPI /agent/query endpoint (EXISTING)
  → LangChain ReACT Agent (EXISTING, no changes)
  → MCP Tool Discovery (NOW discovers 2 tools: list_top_deals + get_forecast)
  → Agent reasons and selects get_forecast tool
  → Tool invocation queries SQLite forecasts table (NEW)
  → Agent synthesizes natural language response with forecast data
  → Return to user
```

### File Structure Requirements

**Files to UPDATE (from Story 1.1):**
```
salesflow_agent/
  mcp/
    crm_server.py            # ADD get_forecast tool definition
data/
  crm.db                     # ADD forecasts table
  seed_data.sql              # ADD forecast seed data
```

**Files UNCHANGED:**
```
salesflow_agent/
  main.py                    # No changes - same endpoint
  agent/
    react_agent.py           # No changes - dynamic discovery handles new tool
    tools.py                 # No changes - MCP client already generic
  mcp/
    client.py                # No changes - discovers tools dynamically
```

**New Files (if not already created in Story 1.1):**
```
None - this story extends existing infrastructure
```

### Critical Implementation Details

#### 1. FastMCP CRM Server Update (`salesflow_agent/mcp/crm_server.py`)
**REQUIRED CHANGE**: Add new tool definition for forecast retrieval.

```python
# ADD this new tool alongside existing list_top_deals:

@mcp.tool()
def get_forecast(quarter: str) -> dict:
    """
    Get sales forecast data for a specific quarter.
    
    Args:
        quarter: Quarter identifier (e.g., 'Q1', 'Q2', 'Q3', 'Q4')
    
    Returns:
        Forecast data including total projected revenue, 
        confidence level, and breakdown by category
    """
    # Query SQLite forecasts table
    # Return structured forecast data for the agent to present
    pass  # Implementation should query crm.db forecasts table
```

**Tool Metadata Requirements:**
- **Name**: `get_forecast` (lowercase, snake_case)
- **Description**: Must clearly state it returns forecast data by quarter
- **Parameters**: Single `quarter` string parameter (e.g., "Q1", "Q2", "Q3", "Q4")
- **Return Type**: Structured dict with forecast amount, confidence, breakdown

**Example Tool Response Format:**
```python
{
    "quarter": "Q3",
    "total_forecast": 2500000,
    "currency": "USD",
    "confidence": "high",
    "breakdown": {
        "new_business": 1500000,
        "expansion": 750000,
        "renewals": 250000
    },
    "last_updated": "2026-08-01"
}
```

#### 2. SQLite Schema Update (`data/seed_data.sql`)
**REQUIRED CHANGE**: Add forecasts table and seed data.

```sql
-- ADD this table definition:

CREATE TABLE IF NOT EXISTS forecasts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quarter TEXT NOT NULL UNIQUE,          -- e.g., 'Q1', 'Q2', 'Q3', 'Q4'
    year INTEGER NOT NULL,                 -- e.g., 2026
    total_forecast INTEGER NOT NULL,       -- Total projected revenue in cents
    new_business INTEGER NOT NULL,         -- New business component
    expansion INTEGER NOT NULL,            -- Expansion component
    renewals INTEGER NOT NULL,             -- Renewals component
    confidence TEXT NOT NULL,              -- 'high', 'medium', 'low'
    last_updated TEXT NOT NULL,            -- ISO 8601 date
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ADD seed data for Q1-Q4 2026:

INSERT INTO forecasts (quarter, year, total_forecast, new_business, expansion, renewals, confidence, last_updated) VALUES
    ('Q1', 2026, 180000000, 110000000, 45000000, 25000000, 'high', '2026-01-15'),
    ('Q2', 2026, 220000000, 130000000, 60000000, 30000000, 'high', '2026-04-15'),
    ('Q3', 2026, 250000000, 150000000, 75000000, 25000000, 'medium', '2026-07-15'),
    ('Q4', 2026, 300000000, 180000000, 90000000, 30000000, 'medium', '2026-10-15');
```

**Schema Design Notes:**
- Store amounts in **cents** (INTEGER) to avoid floating-point errors
- Quarter format: `Q1`, `Q2`, `Q3`, `Q4` (matches user query patterns)
- Confidence levels: `high`, `medium`, `low` (for future agent reasoning)
- Breakdown fields support drill-down questions (future stories)

#### 3. Agent Integration (NO CODE CHANGES REQUIRED)
The existing LangChain ReACT agent from Story 1.1 automatically discovers the new `get_forecast` tool through MCP discovery. No agent code changes are needed.

**Verification:**
- Run MCP server and check tool metadata includes both `list_top_deals` AND `get_forecast`
- Agent logs should show 2 tools discovered on startup (not just 1)
- Agent should correctly select `get_forecast` when user asks forecast questions

### Testing Requirements

**Acceptance Test Scenarios:**
1. **Happy Path - Q3**: User asks "What's the forecast for Q3?" → Agent returns Q3 forecast with amount
2. **Variation - Q1**: User asks "Show me Q1 forecast" → Agent handles alternate phrasing
3. **Natural Language**: User asks "What are we projecting for the third quarter?" → Agent maps to Q3
4. **Multiple Tools**: User asks "What are my top deals and Q3 forecast?" → Agent calls both tools (stretch goal)
5. **Edge Case - Invalid Quarter**: User asks "What's the forecast for Q5?" → Agent handles gracefully (no such quarter)

**Testing Approach:**
- **Manual API Testing**: Use `curl` or Postman to send forecast queries to `/agent/query`
- **Tool Discovery Validation**: Check MCP server logs/metadata shows 2 tools registered
- **Agent Reasoning Trace**: Verify agent selects `get_forecast` tool (not `list_top_deals`) for forecast questions
- **Data Accuracy**: Confirm returned forecast matches seeded Q3 data in database

**Test Data Validation:**
```bash
# Verify seeded forecast data:
sqlite3 data/crm.db "SELECT * FROM forecasts WHERE quarter='Q3';"

# Expected output:
# id=3, quarter='Q3', year=2026, total_forecast=250000000, 
# new_business=150000000, expansion=75000000, renewals=25000000,
# confidence='medium', last_updated='2026-07-15'
```

### Success Criteria Mapping
This story directly implements:
- **FR-2**: Grounded CRM tool invocation (extends to forecast data type)
- **FR-6**: FastMCP discovery of CRM tools (now discovers forecast tool)
- **FR-7**: Mock CRM data retrieval (extends to forecast retrieval with quarterly filtering)
- **SM-1**: Demo completes a natural language CRM query end to end (forecast variant)
- **SM-4**: MCP discovery flow detects at least one CRM tool (now detects 2+ tools)

### Dependencies
- **Upstream**: Story 1.1 (Conversational pipeline query) MUST be complete
  - Requires: FastAPI app, LangChain agent, MCP client, FastMCP server, SQLite setup
- **Downstream**: Story 1.4 (Discover MCP tools dynamically) may add tool introspection UI

### Known Constraints
- **Budget**: Forecast queries use same Claude API as Story 1.1 - no additional LLM cost
- **Quarter Format**: Support only Q1-Q4 format initially (not "third quarter" string matching)
- **Currency**: All forecasts in USD, amounts stored in cents
- **Fiscal Year**: Assume calendar year (Q1 = Jan-Mar) for demo simplicity
- **Historical Data**: Only seed current year forecasts (2026) - no historical quarters

## Implementation Notes for Developer

### Critical Success Factors
1. **No Agent Changes**: If you find yourself modifying the agent code, STOP. The existing agent should discover the new tool automatically.
2. **Tool Description Quality**: The `get_forecast` tool description must clearly state it handles quarterly forecast data. Poor descriptions cause tool selection errors.
3. **Data Consistency**: Forecast amounts must be in cents (INTEGER) and formatted consistently across seed data.
4. **MCP Server Restart**: After adding the new tool, restart the FastMCP server for discovery to pick up changes.

### Recommended Development Sequence
1. **Phase 1: Database Schema** (15 mins)
   - Add forecasts table to `data/seed_data.sql`
   - Seed Q1-Q4 2026 forecast data
   - Rebuild `data/crm.db`: `rm data/crm.db && sqlite3 data/crm.db < data/seed_data.sql`
   - Verify with: `sqlite3 data/crm.db "SELECT * FROM forecasts;"`

2. **Phase 2: FastMCP Tool** (30 mins)
   - Add `get_forecast` function to `salesflow_agent/mcp/crm_server.py`
   - Implement SQLite query to fetch forecast by quarter
   - Format response as structured dict
   - Test tool independently with MCP client

3. **Phase 3: Tool Discovery Validation** (15 mins)
   - Restart FastMCP server
   - Check MCP metadata endpoint shows both tools: `list_top_deals` AND `get_forecast`
   - Verify tool parameter schema is correct (quarter: string)

4. **Phase 4: Agent Integration Testing** (20 mins)
   - Start both FastMCP server and FastAPI app
   - Send test query: `POST /agent/query {"query": "What's the forecast for Q3?"}`
   - Verify agent selects `get_forecast` tool (check agent reasoning trace)
   - Confirm response includes Q3 forecast data

5. **Phase 5: Acceptance Testing** (15 mins)
   - Test all acceptance criteria scenarios
   - Validate natural language variations work
   - Check error handling for invalid quarters

### Potential Pitfalls to Avoid
- **Agent Code Modification**: DO NOT modify `react_agent.py` or `tools.py`. Tool discovery is automatic.
- **Hardcoded Quarter Mapping**: DO NOT add Q3 → "third quarter" string parsing in the agent. Keep it simple: support Q1-Q4 format only.
- **Floating-Point Currency**: DO NOT use FLOAT for forecast amounts. Use INTEGER (cents) to avoid precision errors.
- **Tool Name Mismatch**: Ensure tool function name matches what's registered with FastMCP (use `@mcp.tool()` decorator correctly).
- **Missing Tool Description**: A vague tool description will cause the agent to ignore the tool or select it incorrectly.

### Example Agent Trace (Expected Output)
```
User: "What's the forecast for Q3?"

Agent Reasoning:
  Thought: The user is asking for forecast data for Q3. I should use the forecast retrieval tool.
  Action: get_forecast
  Action Input: {"quarter": "Q3"}
  
Tool Response:
  {
    "quarter": "Q3",
    "total_forecast": 2500000,
    "currency": "USD",
    "confidence": "medium",
    "breakdown": {
      "new_business": 1500000,
      "expansion": 750000,
      "renewals": 250000
    },
    "last_updated": "2026-07-15"
  }
  
Final Answer:
  "The Q3 2026 forecast is $2.5M with medium confidence. 
   This breaks down into $1.5M from new business, $750K from expansions, 
   and $250K from renewals. The forecast was last updated on July 15, 2026."
```

### Environment Setup
**No new environment variables needed** - reuse existing setup from Story 1.1:
```bash
# Same .env file from Story 1.1:
ANTHROPIC_API_KEY=sk-ant-...
MCP_SERVER_URL=http://localhost:8001
```

### Code Quality Checklist
- [ ] `get_forecast` function has clear docstring with parameter descriptions
- [ ] SQLite query uses parameterized statements (prevent SQL injection)
- [ ] Forecast amounts are returned in standard format (dollars, not cents) for user presentation
- [ ] Tool response includes all required fields: quarter, total_forecast, confidence, breakdown
- [ ] Error handling for missing quarters (e.g., query for Q5 or invalid quarter)
- [ ] MCP server logs show tool registration on startup
- [ ] No agent code modifications (verify git diff shows no changes to react_agent.py)

### Integration with Story 1.1
**Shared Infrastructure (DO NOT DUPLICATE):**
- FastAPI app and `/agent/query` endpoint
- LangChain ReACT agent configuration
- MCP client and tool discovery logic
- SQLite database connection logic
- Environment variable loading

**New Components (ADD to existing):**
- `get_forecast` tool definition in FastMCP server
- `forecasts` table in SQLite schema
- Q1-Q4 2026 forecast seed data

### Validation Checklist Before Marking Complete
- [ ] Forecasts table exists in `data/crm.db` with 4 seeded quarters
- [ ] FastMCP server exposes `get_forecast` tool (check MCP metadata)
- [ ] Agent discovers 2 tools on startup: `list_top_deals` + `get_forecast`
- [ ] User query "What's the forecast for Q3?" returns correct Q3 data
- [ ] Agent reasoning trace shows tool selection and invocation
- [ ] Response is natural language with properly formatted currency
- [ ] No agent code files modified (git diff check)
- [ ] README updated with forecast query examples (optional but recommended)

## References

### Architecture Document
[Source: salesflow-agent-architecture.md#FastMCP CRM Server]
- FastMCP server exposes mock CRM and forecast tools via discoverable metadata
- Tools are backed by SQLite seeded data
- Agent discovers tools at runtime without hardcoded definitions

[Source: salesflow-agent-architecture.md#MCP Client Integration]
- Agent uses MCP metadata to populate tool descriptors dynamically
- Tools appear as dynamic functions rather than hardcoded actions
- Enables extensibility: new tools added to MCP server become available to agent without code changes

### PRD Document
[Source: salesflow-agent-prd.md#FR-6: FastMCP discovery of CRM tools]
- At least one mock CRM tool is discovered automatically
- Tool descriptions are visible in logs or agent tool metadata

[Source: salesflow-agent-prd.md#FR-7: Mock CRM data retrieval]
- Tool calls support basic filtering (e.g., forecast by quarter)
- System returns structured sales data from SQLite in response to agent calls

### Epics and Stories Document
[Source: salesflow-agent-epics-stories.md#Story 2: Forecast question via MCP]
- Acceptance: Agent calls the MCP forecast tool
- Acceptance: Answer includes a forecast number or summary for Q3

### Previous Story Intelligence
[Source: 1-1-conversational-pipeline-query.md]
- MCP discovery pattern established: agent discovers tools from FastMCP metadata at startup
- ReACT agent pattern proven: agent reasons about tool selection based on user query
- SQLite seeded data pattern: use seed_data.sql script for reproducible database setup
- Testing approach: manual API testing via curl/Postman, validate agent reasoning trace
- **Key Learning**: Tool descriptions are critical - vague descriptions cause tool selection errors

## Dev Agent Record

### Agent Model Used
Claude 3.5 Sonnet (via GitHub Copilot)

### Debug Log References
- Will be added during implementation

### Completion Notes List
- Will be added during implementation

### File List
**Files to be modified:**
- `salesflow_agent/mcp/crm_server.py` - Add `get_forecast` tool
- `data/seed_data.sql` - Add forecasts table schema and seed data
- `data/crm.db` - Rebuild after schema update

**Files unchanged (verify in git diff):**
- `salesflow_agent/main.py`
- `salesflow_agent/agent/react_agent.py`
- `salesflow_agent/agent/tools.py`
- `salesflow_agent/mcp/client.py`
