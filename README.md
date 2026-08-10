# SalesFlow Agent

GenAI Sales Assistant demonstrating four integrated AI patterns:
- **ReACT Agent** — LLM reasoning and dynamic tool calling via LangChain
- **RAG** — Retrieval Augmented Generation with FAISS vector search
- **MCP** — Model Context Protocol for runtime tool discovery
- **Workflow Orchestration** — BPMN lead qualification via Zeebe

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/sv-92/sales-agent.git
cd sales-agent
pip install -e .  # or: uv sync

# 2. Set up environment
cp .env.example .env
# Edit .env with your API keys

# 3. Run (MCP server starts automatically)
python -m salesflow_agent
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/agent/query` | Natural language sales questions |
| POST | `/leads/qualify` | Submit lead for qualification |
| GET | `/health` | Health check |
| GET | `/docs` | Interactive API docs (Swagger) |

## Example Queries

```bash
# Pipeline question (MCP → CRM)
curl -X POST http://localhost:8000/agent/query \
  -H "Content-Type: application/json" \
  -d '{"message": "What are my top 5 deals by value?"}'

# Objection handling (RAG → Knowledge Base)
curl -X POST http://localhost:8000/agent/query \
  -H "Content-Type: application/json" \
  -d '{"message": "How should I handle a pricing objection from an enterprise customer?"}'

# Lead qualification (Workflow → Enrich + Score)
curl -X POST http://localhost:8000/leads/qualify \
  -H "Content-Type: application/json" \
  -d '{"company_name": "Acme Corp", "industry": "Technology", "size": "Enterprise"}'
```

## Architecture

```
User → FastAPI → LangChain ReACT Agent
                      ├── MCP Client → FastMCP Server → SQLite CRM
                      ├── RAG Retriever → FAISS → Knowledge Docs
                      └── Workflow Client → Zeebe → Workers
```

## Project Structure

```
salesflow_agent/
  __main__.py          # Entry point
  main.py              # FastAPI app
  agent/
    react_agent.py     # LangChain ReACT agent
    tools.py           # RAG tool wrapper
  mcp/
    client.py          # MCP tool discovery
    crm_server.py      # FastMCP CRM server
  rag/
    index_builder.py   # FAISS index builder
    retriever.py       # Retriever interface
  workflows/
    client.py          # Zeebe client
    workers/
      enrichment_worker.py
      scoring_worker.py
  data/
    seed.py            # Database seeding
data/
  seed_data.sql        # Mock CRM data
  knowledge/           # Sales playbook documents
  faiss_index/         # Generated (gitignored)
```

## Optional: Zeebe Workflow Engine

```bash
# Start Zeebe (Docker required)
docker-compose up -d

# The app works without Zeebe — lead qualification falls back to direct execution
```

## Tech Stack
- Python 3.11+, FastAPI, LangChain, Claude Sonnet 4.5
- FAISS (vector search), FastMCP (tool discovery)
- Zeebe/Camunda (workflow), SQLite (mock CRM)
