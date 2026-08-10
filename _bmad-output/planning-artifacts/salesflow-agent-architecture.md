# Architecture: SalesFlow Agent

## Overview
SalesFlow Agent is a local Python prototype built around four integrated GenAI patterns:
- ReACT conversational agent for agent reasoning and tool calling.
- RAG search over a local FAISS knowledge base.
- MCP discovery of mock CRM tools served by FastMCP.
- BPMN workflow orchestration via Zeebe/Camunda and pyzeebe workers.

The architecture is intentionally simple and end-to-end: a single FastAPI host orchestrates user requests, the LangChain agent routes work to discovery and retrieval layers, and a local Zeebe broker executes the lead qualification workflow.

## Core Components

### 1. FastAPI Application
- Entry point for the demo.
- Exposes HTTP endpoints for conversational queries and workflow triggers.
- Boots shared services: LLM client, embeddings client, FAISS store, MCP client, workflow client.
- Runs in the same Python process as the agent and business logic.

### 2. LangChain ReACT Agent
- Uses Claude via `langchain-anthropic`.
- Receives natural language input and decides whether to use:
  - Retrieval tool (RAG content)
  - MCP CRM tools
  - Direct response generation
- Synthesizes responses into coherent answers.

### 3. RAG / FAISS Knowledge Store
- Embeds sales playbook and guidance documents.
- Stores embeddings in FAISS for local semantic search.
- Provides a retrieval interface to the agent and workflow components.
- Supports local rebuild or warm startup from seeded content.

### 4. FastMCP CRM Server
- A separate process exposing mock CRM and forecast tools.
- Backed by SQLite seeded with deals, accounts, contacts, leads, and forecast records.
- Exposes discoverable tool metadata used by the agent.
- Demonstrates the extensible MCP pattern.

### 5. MCP Client Integration
- The agent uses MCP metadata to populate tool descriptors.
- Tools appear to the agent as dynamic functions rather than hardcoded actions.
- Enables the agent to call mock CRM operations such as `list_deals`, `get_forecast`, `search_accounts`.

### 6. Zeebe / Camunda Workflow Engine
- Runs locally in Docker via `docker-compose up`.
- Hosts a BPMN process that qualifies new leads.
- The workflow includes service tasks for enrichment and scoring.

### 7. pyzeebe Workers
- Python worker processes subscribe to Zeebe service tasks.
- Workers perform:
  - lead enrichment using RAG knowledge search
  - LLM scoring of fit and intent
  - outcome routing logic for auto-qualification or review
- Worker code is simple and demo-focused.

### 8. SQLite Mock Data Store
- Stores seeded demo data for CRM and lead records.
- Powers FastMCP and optionally workflow persistence.
- Maintains the local-only constraint.

## Data Flow

### Pipeline Question Flow
1. User submits a natural language query to FastAPI.
2. FastAPI passes the query to the LangChain ReACT agent.
3. Agent discovers available MCP tools from FastMCP metadata.
4. If the query requires CRM data, the agent calls the appropriate MCP tool.
5. The tool returns structured data from SQLite.
6. If the question benefits from knowledge context, the agent also retrieves RAG content.
7. Agent synthesizes the answer and returns it to the user.

### RAG Question Flow
1. User asks a question that should leverage company knowledge.
2. FastAPI invokes the RAG retriever.
3. RAG search returns top-N document chunks from FAISS.
4. The agent uses those chunks as context for answer generation.
5. The response is returned with grounded guidance.

### Lead Qualification Workflow Flow
1. A new lead is submitted to an API endpoint or CLI command.
2. FastAPI starts the Zeebe BPMN process.
3. A pyzeebe worker pulls the enrichment task and queries FAISS for relevant content.
4. Another worker calls Claude to score the lead.
5. Workflow routing decides auto-qualified vs human review.
6. The result is stored or logged for inspection.

## Deployment / Run Model
- `docker-compose up` starts Zeebe / Camunda locally.
- `python -m salesflow_agent` starts the FastAPI app and workers.
- The app needs only local resources plus the Anthropic Claude API key.
- No authentication, no external database, and no multi-tenant plumbing.

## Integration Points
- **LLM API**: Claude via LangChain. Use a lightweight model and prompt design to contain cost.
- **Embeddings**: Anthropic/OpenAI embeddings for RAG. Choose the lower-cost provider that works with the demo.
- **MCP**: FastMCP server runs independently and exposes its own ports.
- **Workflow**: Zeebe engine runs in Docker and communicates with Python workers over gRPC.

## Architectural Decisions
- Prefer a single FastAPI host to keep the demo simple.
- Keep the agent and knowledge retrieval local rather than using remote vector stores.
- Use MCP discovery to demonstrate extensibility without hardcoding tool interfaces.
- Build the workflow as a separate, observable layer to show BPMN integration with AI.
- Avoid complex UI; focus on the API and prototype behavior.

## Risks and Mitigations
- **LLM cost risk**: Use concise prompts, low-cost Claude model, and limit test queries. Keep developer testing narrow.
- **Tool discovery complexity**: Start with one well-defined MCP server and one strong CRM tool set.
- **Workflow orchestration overhead**: Model a small BPMN process with only 3–4 steps and simple worker tasks.
- **Local Docker friction**: Provide `docker-compose` and clear startup instructions so reviewers can run end to end.

## Recommended Runtime Structure
- `salesflow_agent/` package contains app, agent, rag, mcp client, and workflow code.
- `docker-compose.yml` defines the Zeebe broker and required console components.
- `data/` contains seeded SQLite fixtures and knowledge documents.
- `scripts/` contains startup helpers and index rebuild utilities.
