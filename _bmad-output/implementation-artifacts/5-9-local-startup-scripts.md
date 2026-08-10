---
story_id: "5.9"
epic: "Epic 5: Local Developer Experience"
title: "Local startup experience"
status: "ready-for-dev"
created: 2026-08-10
updated: 2026-08-10
---

# Story 5.9: Local startup experience

## User Story
**As a** developer  
**I want to** run `docker-compose up` and `python -m salesflow_agent`  
**So that** I can start the demo locally with minimal commands

## Business Value
This story ensures the demo is immediately runnable by the interviewer or anyone reviewing the project. A clean local startup experience demonstrates engineering craftsmanship and makes the technical discussion more interactive. If Peter can clone and run it in under 5 minutes, it demonstrates operational excellence.

## Acceptance Criteria
```gherkin
Given the repository is cloned and dependencies installed
When the user runs `docker-compose up -d`
Then Zeebe starts in Docker without errors
And Zeebe is accessible on port 26500

When the user runs `python -m salesflow_agent`
Then the FastAPI app starts without errors
And the MCP CRM server starts as a subprocess
And the agent endpoints are reachable on http://localhost:8000
And the FAISS index is loaded (or built if missing)
And startup logs show successful initialization of all components
```

## Technical Requirements

### Stack & Dependencies
- **Docker Compose**: For Zeebe engine
- **Python**: Entry point via `__main__.py`
- **uvicorn**: ASGI server for FastAPI
- **Environment**: `.env` file with API keys

### File Structure Requirements

**Expected New Files:**
```
salesflow_agent/
  __main__.py                 # Entry point: python -m salesflow_agent
pyproject.toml                # Python project config with dependencies
.env.example                  # Template for required environment variables
Makefile                      # Optional convenience commands
```

### Critical Implementation Details

#### 1. Entry Point (`salesflow_agent/__main__.py`)
```python
# Must:
# - Load environment variables from .env
# - Start FastMCP server as subprocess (separate port)
# - Build FAISS index if not present
# - Start FastAPI app with uvicorn
# - Handle graceful shutdown (kill MCP subprocess)
# - Print clear startup banner with URLs
```

#### 2. Project Config (`pyproject.toml`)
```toml
# Must include:
# - All dependencies with version pins
# - Python 3.11+ requirement
# - Project metadata
# - Script entry point
```

#### 3. Environment Template (`.env.example`)
```bash
# Must document:
# ANTHROPIC_API_KEY=your-key-here
# OPENAI_API_KEY=your-key-here (if using OpenAI embeddings)
# MCP_SERVER_PORT=8001
# ZEEBE_ADDRESS=localhost:26500
```

### Testing Requirements

1. **Clean Start**: App starts from fresh clone + `uv sync` + `python -m salesflow_agent`
2. **Missing Env**: Clear error message if ANTHROPIC_API_KEY is missing
3. **No Docker**: App starts without Zeebe (workflow features degraded, rest works)
4. **Port Conflicts**: Clear error if ports 8000 or 8001 are in use

### Dependencies
- **Upstream**: All other stories (this packages them together)
- **Downstream**: Story 5.10 (Demo Fixtures)

### Known Constraints
- **Graceful Degradation**: App should start even if Zeebe is down (log warning, disable workflow)
- **Single Command**: Minimize steps between clone and running demo
- **Cross-Platform**: Should work on macOS and Linux (primary dev environments)
