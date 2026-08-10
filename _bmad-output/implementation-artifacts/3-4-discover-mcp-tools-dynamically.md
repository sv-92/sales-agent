---
story_id: "3.4"
epic: "Epic 3: MCP CRM Discovery"
title: "Discover MCP tools dynamically"
status: "ready-for-dev"
created: 2026-08-09
updated: 2026-08-09
---

# Story 3.4: Discover MCP tools dynamically

## User Story
**As a** developer  
**I want to** start the app and see MCP CRM tools discovered at runtime  
**So that** I can add new sources without code changes

## Business Value
This story enables the extensibility pattern that makes the agent truly dynamic. By discovering MCP tools at runtime rather than hardcoding tool definitions, the system becomes maintainable and scalable. This story demonstrates the core value proposition of MCP: plug-and-play integration with new data sources. It validates FR-6 (FastMCP discovery of CRM tools) from the PRD and proves the architectural decision to "use MCP discovery to demonstrate extensibility without hardcoding tool interfaces."

This is a critical infrastructure story that unblocks all subsequent MCP-dependent features and demonstrates best practices for agentic systems.

## Acceptance Criteria
```gherkin
Given the FastAPI application is starting up
And the FastMCP CRM server is running
When the application initializes the MCP client
Then the agent logs or exposes tool metadata from FastMCP discovery
And at least one CRM tool is discovered automatically
And the tool metadata includes name, description, and parameter schema
And the discovered tools are registered with the LangChain agent
And no CRM tool definitions are hardcoded in the agent code
```

## Technical Requirements

### Stack & Dependencies
- **Python**: 3.11+
- **FastMCP**: For MCP server framework (separate process)
- **MCP SDK/Client**: For discovering and invoking MCP tools
- **LangChain**: Tool integration layer
- **Pydantic**: Schema validation for tool parameters
- **Logging**: Python logging for tool discovery traces

### Architecture Compliance

#### Component Structure
This story implements the **MCP Client Integration** component from the architecture.

**Critical Architecture Points:**
1. **Dynamic Tool Discovery**: Agent must use MCP metadata to populate tool descriptors - NO hardcoded tool definitions
2. **Separation of Concerns**: MCP server runs as a separate process, not in FastAPI app
3. **Observable Discovery**: Tool discovery must be logged and visible to developers
4. **LangChain Integration**: Discovered tools must be converted to LangChain tool format for agent use
5. **Extensible Pattern**: Adding a new MCP tool should require zero agent code changes

#### Data Flow (from Architecture)
```
App Startup → MCP Client Init → Query FastMCP Server for Metadata
  → Receive Tool Definitions (name, description, params)
  → Convert to LangChain Tool Format
  → Register Tools with ReACT Agent
  → Log Discovery Summary
  → Agent Ready with Dynamic Tools
```

### File Structure Requirements

**Expected New/Modified Files:**
```
salesflow_agent/
  mcp/
    __init__.py
    client.py                # MCP client for tool discovery (NEW)
    server.py                # FastMCP server with tool definitions (MODIFY)
    types.py                 # Type definitions for MCP tools (NEW)
  agent/
    react_agent.py          # Agent initialization with dynamic tools (MODIFY)
  config.py                 # Configuration for MCP server endpoint (NEW)
tests/
  test_mcp_discovery.py     # Test tool discovery flow (NEW)
```

### Critical Implementation Details

#### 1. MCP Client (`salesflow_agent/mcp/client.py`)
**Purpose**: Discover available tools from FastMCP server on startup and convert to LangChain format.

**Must implement**:
```python
class MCPClient:
    """
    Client for discovering and invoking MCP tools.
    
    This client connects to a FastMCP server, queries available tools,
    converts tool metadata to LangChain Tool format, and handles invocations.
    """
    
    def __init__(self, server_url: str):
        """Initialize MCP client with FastMCP server URL."""
        
    async def discover_tools(self) -> List[LangChainTool]:
        """
        Query FastMCP server for available tools.
        
        Returns:
            List of LangChain-compatible tool objects
            
        Must:
        - Query FastMCP /tools or equivalent discovery endpoint
        - Parse tool metadata (name, description, parameters)
        - Convert parameter schemas to Pydantic models
        - Create LangChain Tool instances
        - Log each discovered tool with name and description
        """
        
    async def invoke_tool(self, tool_name: str, params: dict) -> Any:
        """
        Invoke a specific MCP tool with parameters.
        
        Args:
            tool_name: Name of the tool to invoke
            params: Tool parameters as dict
            
        Returns:
            Tool execution result
            
        Must:
        - Validate params against tool schema
        - Call FastMCP tool endpoint
        - Handle errors gracefully
        - Return structured result
        """
        
    def log_discovery_summary(self, tools: List[LangChainTool]):
        """
        Log summary of discovered tools for developer visibility.
        
        Must include:
        - Total count of tools discovered
        - Tool names and brief descriptions
        - Server URL and timestamp
        """
```

**Key Requirements**:
- Use async/await for network calls
- Implement proper error handling for server unavailable
- Convert FastMCP schemas to Pydantic models dynamically
- Log all discovery events at INFO level
- Return LangChain-compatible Tool objects

#### 2. FastMCP Server (`salesflow_agent/mcp/server.py`)
**Purpose**: Expose CRM tools via FastMCP protocol with proper metadata.

**Must implement**:
```python
from fastmcp import FastMCP

mcp = FastMCP("CRM Tools")

@mcp.tool()
async def list_top_deals(limit: int = 5) -> list[dict]:
    """
    Get top deals by value from CRM.
    
    Args:
        limit: Maximum number of deals to return (default: 5)
        
    Returns:
        List of deals with name, amount, stage
    """
    # Implementation here
    
@mcp.tool()
async def get_forecast(quarter: str) -> dict:
    """
    Get sales forecast for a specific quarter.
    
    Args:
        quarter: Quarter identifier (e.g., "Q3", "Q4")
        
    Returns:
        Forecast data including total, confidence, breakdown
    """
    # Implementation here
    
@mcp.tool()
async def search_accounts(query: str, limit: int = 10) -> list[dict]:
    """
    Search for accounts by name or industry.
    
    Args:
        query: Search term for account name or industry
        limit: Maximum results to return
        
    Returns:
        List of matching accounts with name, industry, revenue
    """
    # Implementation here
```

**Key Requirements**:
- Use FastMCP decorators for tool definitions
- Include detailed docstrings (used for tool descriptions)
- Use type hints for all parameters (used for schema generation)
- Return structured data (dicts/lists, not raw strings)
- Run on separate port from FastAPI app (e.g., port 8001)

#### 3. Agent Initialization (`salesflow_agent/agent/react_agent.py`)
**Purpose**: Initialize ReACT agent with dynamically discovered tools.

**Must modify**:
```python
async def initialize_agent() -> AgentExecutor:
    """
    Initialize LangChain ReACT agent with MCP-discovered tools.
    
    Steps:
    1. Create MCP client instance
    2. Discover all available tools
    3. Log discovery summary
    4. Initialize Claude LLM
    5. Create agent with dynamic tools
    6. Return configured agent executor
    """
    # Get MCP server URL from config
    mcp_url = get_config().mcp_server_url
    
    # Discover tools
    mcp_client = MCPClient(mcp_url)
    tools = await mcp_client.discover_tools()
    
    # Log what we found
    logger.info(f"Discovered {len(tools)} MCP tools from {mcp_url}")
    for tool in tools:
        logger.info(f"  - {tool.name}: {tool.description}")
    
    # Initialize agent with discovered tools
    llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
    agent = create_react_agent(llm, tools)
    
    return AgentExecutor(agent=agent, tools=tools)
```

**Key Requirements**:
- Call discovery on app startup, not per request
- Log all discovered tools before agent creation
- Handle discovery failures gracefully (log error, continue with empty tools)
- Store MCP client instance for later tool invocations
- Support agent reload if MCP server restarts

#### 4. Configuration (`salesflow_agent/config.py`)
**Purpose**: Centralize MCP server configuration.

**Must implement**:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings from environment and config files."""
    
    # MCP Configuration
    mcp_server_url: str = "http://localhost:8001"
    mcp_discovery_timeout: int = 5  # seconds
    mcp_retry_attempts: int = 3
    
    # LLM Configuration
    anthropic_api_key: str
    model_name: str = "claude-3-5-sonnet-20241022"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

def get_config() -> Settings:
    """Get singleton configuration instance."""
    return Settings()
```

### Testing Requirements

**Acceptance Test Scenarios:**

1. **Successful Discovery**:
   - Given: MCP server running with 3 defined tools
   - When: App starts and discovers tools
   - Then: Agent logs show 3 tools discovered with names and descriptions
   - And: Agent can invoke any discovered tool

2. **Server Unavailable**:
   - Given: MCP server not running
   - When: App attempts tool discovery
   - Then: Discovery logs error but app starts successfully
   - And: Agent operates with empty tool list

3. **Multiple Tool Types**:
   - Given: MCP server exposes list_top_deals, get_forecast, search_accounts
   - When: Discovery runs
   - Then: All 3 tools are registered with correct parameter schemas
   - And: Agent can correctly invoke each tool type

4. **Tool Metadata Validation**:
   - Given: Discovered tool from MCP server
   - When: Tool metadata is inspected
   - Then: Tool has valid name (non-empty string)
   - And: Tool has description (non-empty string)
   - And: Tool has parameter schema (Pydantic model or JSON schema)

5. **No Hardcoded Tools**:
   - Given: Agent initialization code
   - When: Code is inspected
   - Then: No hardcoded tool definitions exist
   - And: All tools come from MCP discovery

**Testing Approach**:
- Unit tests for MCP client discovery logic
- Integration tests for end-to-end discovery flow
- Mock FastMCP server for testing edge cases
- Manual verification of discovery logs during app startup

**Test Data Requirements**:
- Mock FastMCP server returning 3 sample tools
- Test fixtures for tool metadata schemas
- Sample tool invocation requests and responses

### Previous Story Intelligence

**From Story 1-1 (Conversational pipeline query)**:
- MCP client integration was mentioned but not fully implemented
- Agent initialization pattern established in `react_agent.py`
- Tool registration pattern with LangChain already exists
- SQLite CRM data structure is established
- FastAPI startup lifecycle can be extended for discovery

**From Story 1-2 (Forecast question via MCP)**:
- Forecast tool may already be defined in MCP server
- Tool invocation pattern is established
- Need to ensure discovery picks up all existing tools

**Key Learnings to Apply**:
- Keep discovery async and non-blocking
- Log extensively for developer debugging
- Fail gracefully if MCP server is down
- Use existing LangChain tool patterns for consistency

### Edge Cases to Handle

1. **MCP Server Restarts**: Agent should handle server becoming unavailable mid-session
2. **Tool Schema Changes**: If server changes tool schemas, agent should detect on restart
3. **Network Delays**: Discovery should timeout gracefully if server is slow
4. **Empty Tool List**: Server with zero tools should not crash agent
5. **Malformed Tool Metadata**: Invalid schemas should be logged and skipped

### Implementation Guidance

**Phase 1: MCP Client Foundation**
- Implement MCPClient class with discover_tools method
- Add basic error handling and logging
- Create mock FastMCP server for testing
- Validate tool metadata parsing

**Phase 2: LangChain Integration**
- Convert MCP tool metadata to LangChain Tool format
- Test tool registration with mock agent
- Implement invoke_tool method for execution
- Add comprehensive logging

**Phase 3: Agent Initialization**
- Modify agent init to call MCP discovery
- Add discovery to app startup sequence
- Implement graceful degradation if discovery fails
- Add discovery metrics/observability

**Phase 4: Testing & Validation**
- Write unit tests for discovery logic
- Add integration tests with real FastMCP server
- Manual testing of startup logs
- Verify no hardcoded tools remain

### Success Criteria

✅ **Story is DONE when**:
- App startup logs show all MCP tools discovered
- Agent can invoke any discovered tool successfully
- No tool definitions are hardcoded in agent code
- Discovery works with FastMCP server on separate port
- Tool metadata includes name, description, and parameters
- Discovery fails gracefully when server unavailable
- All acceptance criteria pass
- Code review confirms no hardcoded tool patterns

### Dependencies & Blockers

**Depends On**:
- Story 1-1: Agent and MCP server foundation must exist
- FastMCP server must be running on configured port

**Blocks**:
- All future MCP-based features depend on this discovery pattern
- Story 3-5 and beyond will assume tool discovery is working

**External Dependencies**:
- FastMCP library version compatibility
- MCP protocol stability

### Developer Notes

**Critical Implementation Constraints**:
- DO NOT hardcode any tool definitions in agent code
- ALL tools must come from MCP discovery endpoint
- Discovery MUST happen at app startup, not per request
- Tool invocations MUST use the same MCP client instance
- Logging MUST include tool names and discovery timestamp

**Common Pitfalls to Avoid**:
- Hardcoding tools "temporarily" during development
- Forgetting to convert parameter schemas to Pydantic models
- Blocking app startup if MCP server is down
- Not logging tool discovery for debugging
- Coupling agent code to specific tool names

**Verification Checklist Before Marking Done**:
- [ ] App startup logs show discovered tools
- [ ] Can grep codebase and find ZERO hardcoded tool definitions
- [ ] Discovery works with server on separate port
- [ ] Discovery gracefully handles server unavailable
- [ ] All tools have valid metadata (name, description, params)
- [ ] LangChain agent can invoke discovered tools
- [ ] Tests validate discovery flow
- [ ] Code review confirms no hardcoding

## Related Documentation

**Architecture References**:
- [MCP Client Integration](../planning-artifacts/salesflow-agent-architecture.md#5-mcp-client-integration)
- [FastMCP CRM Server](../planning-artifacts/salesflow-agent-architecture.md#4-fastmcp-crm-server)
- [Architectural Decisions](../planning-artifacts/salesflow-agent-architecture.md#architectural-decisions)

**PRD References**:
- [FR-6: FastMCP discovery of CRM tools](../planning-artifacts/salesflow-agent-prd.md#fr-6-fastmcp-discovery-of-crm-tools)
- [Feature 4.3: MCP-based CRM Data Discovery](../planning-artifacts/salesflow-agent-prd.md#43-mcp-based-crm-data-discovery)

**Epic Context**:
- [Epic 3: MCP CRM Discovery](../planning-artifacts/salesflow-agent-epics-stories.md#epic-3-mcp-crm-discovery)

---

**Status**: ready-for-dev  
**Created**: 2026-08-09  
**Last Updated**: 2026-08-09  
**Estimated Effort**: 4-6 hours  
**Risk Level**: Medium (depends on FastMCP protocol stability)
