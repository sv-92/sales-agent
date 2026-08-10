# Walmart ↔ Personal Copilot Handoff Tracking

## Project Context
- **Project**: SalesFlow Agent - GenAI demo for Pinterest interview with Peter
- **Tech Stack**: Python, FastAPI, LangChain, Claude Sonnet 4.5, FAISS, FastMCP, Zeebe, SQLite
- **Framework**: BMad Method v6.10.0 (spec-driven development)
- **Budget**: $3-5 total (demo quality)
- **GitHub Repo**: https://github.com/sv-92/sales-agent.git

## Environment Split Strategy

### Walmart Copilot (Opus Unlimited - Cost-Free)
**What to do here:**
- ✅ BMad story creation using `bmad-create-story` skill
- ✅ Code implementation using `bmad-quick-dev` or `bmad-dev-story`
- ✅ Architecture planning and spec refinement
- ✅ Documentation writing
- ⚠️ **VPN Restrictions**: Cannot access external APIs, cannot test runtime

**Limitations:**
- No access to Claude API for testing
- No access to PyPI/npm for package installation verification
- Cannot run Docker (Zeebe)
- Cannot test FastAPI endpoints or MCP server

### Personal Copilot (Sonnet 4.5 - Paid)
**What to do here:**
- ✅ Testing and runtime validation
- ✅ Bug fixes from test failures
- ✅ Package installation and dependency resolution
- ✅ Docker compose and Zeebe setup
- ✅ Final integration testing and demo polish

---

## Handoff Protocol

### When Handing Off FROM Walmart TO Personal
**Commit message format**: `[WALMART] Brief description of what was completed`

**In this file, add:**
```markdown
### Handoff [DATE/TIME]
**From**: Walmart Copilot
**Completed**:
- [ List what was done ]

**For Personal Copilot**:
- [ List what needs testing/fixing ]
- [ List any errors or uncertainties ]

**Files Changed**:
- [ List modified files ]
```

### When Handing Off FROM Personal TO Walmart
**Commit message format**: `[PERSONAL] Brief description of fixes/tests`

**In this file, add:**
```markdown
### Handoff [DATE/TIME]
**From**: Personal Copilot
**Test Results**:
- [ What was tested and results ]

**Issues Found**:
- [ List bugs or problems ]

**For Walmart Copilot**:
- [ List what to implement next ]

**Files Changed**:
- [ List modified files ]
```

---

## Current Status

### Latest Handoff
**Date**: 2026-08-10
**From**: Walmart Copilot
**Status**: Full implementation complete — ready for testing on Personal Copilot

**Completed This Session**:
- ✅ Created remaining story files (Stories 5-10)
- ✅ Implemented Epic 1: Agent Core (FastAPI + LangChain ReACT Agent)
- ✅ Implemented Epic 2: RAG Knowledge Base (FAISS + 6 knowledge documents)
- ✅ Implemented Epic 3: MCP CRM Discovery (FastMCP server + dynamic tool discovery)
- ✅ Implemented Epic 4: Workflow Orchestration (Zeebe client + enrichment/scoring workers)
- ✅ Implemented Epic 5: Local Developer Experience (entry point, seed data, README, docker-compose)
- ✅ All 3 user journeys implemented (Pipeline Query, Objection Handling, Lead Qualification)

**For Personal Copilot**:
1. `pip install -e .` (or `uv sync`) — install dependencies
2. Copy `.env.example` to `.env` and add API keys (ANTHROPIC_API_KEY, OPENAI_API_KEY)
3. Run `python -m salesflow_agent` — starts MCP server + FastAPI app
4. Test endpoints:
   - `POST /agent/query` with `{"message": "What are my top 5 deals?"}`
   - `POST /agent/query` with `{"message": "How do I handle pricing objections?"}`
   - `POST /leads/qualify` with `{"company_name": "Acme Corp", "industry": "Technology"}`
5. Fix any import/runtime errors
6. Optional: `docker-compose up -d` for Zeebe workflow (not required — app falls back gracefully)

**Known Uncertainties (Needs Testing)**:
- FastMCP `streamable-http` transport may need URL path adjustment
- `langchain-openai` embeddings require OPENAI_API_KEY (could switch to Anthropic embeddings)
- pyzeebe connection handling when Zeebe is not running
- FAISS index rebuild on first run timing

**Files Changed**:
- `pyproject.toml` — project config and dependencies
- `README.md` — project documentation
- `.env.example` — environment template
- `.gitignore` — ignore patterns
- `docker-compose.yml` — Zeebe setup
- `data/seed_data.sql` — mock CRM data (deals, accounts, contacts, forecasts, leads)
- `data/knowledge/*.md` — 6 sales playbook documents
- `salesflow_agent/` — entire Python package (14 source files)
- `_bmad-output/implementation-artifacts/` — 6 new story files (Stories 5-10)

---

### Previous Handoff

### [2026-08-10] Personal → Walmart
**Completed**:
- BMad setup complete
- Planning artifacts generated and reviewed
- Stories 1-4 created
- Git repository initialized and pushed

**For Walmart Copilot**:
- Create Stories 5-10 using `bmad-create-story [story-id]`
- Start implementing Epic 1 and Epic 3 code
- NO TESTING NEEDED - just create code files
- Commit frequently with `[WALMART]` prefix

**Context Files Available**:
- All planning artifacts in `_bmad-output/planning-artifacts/`
- Resume and project plan in `docs/`
- This handoff tracking file

---

## Tips for Smooth Transitions

### For Walmart Copilot User (Satwik)
1. Pull latest: `git pull origin main` before starting
2. Use BMad skills extensively - they're free with Opus!
3. Don't worry about testing - focus on story specs and code generation
4. Commit often: `git add . && git commit -m "[WALMART] description" && git push`
5. Update this file before each handoff with detailed notes

### For Personal Copilot User (Satwik)
1. Pull latest: `git pull origin main` before starting
2. Focus on running, testing, fixing
3. Keep test runs minimal to save on Sonnet costs
4. Push fixes and update this file with test results
5. Tell Walmart Copilot what to build next

### Cost Optimization
- **Walmart**: Story creation (detailed specs) + implementation (code files)
- **Personal**: Testing (runtime) + bug fixes (minimal iterations)
- This keeps 80%+ of token usage on free Walmart Opus

---

## Emergency Context Recovery

If either Copilot loses context, point it to:
1. This file (`docs/HANDOFF-TRACKING.md`)
2. Latest git commit messages
3. Planning artifacts in `_bmad-output/planning-artifacts/`
4. Story files in `_bmad-output/implementation-artifacts/`

**Quick Context Prompt for Walmart Copilot**:
```
Read docs/HANDOFF-TRACKING.md, docs/README.md, and _bmad-output/planning-artifacts/*.md 
to understand the SalesFlow Agent project. I'm using BMad Method to build a demo for 
Pinterest interview. Continue where the handoff log left off.
```

**Quick Context Prompt for Personal Copilot**:
```
Read docs/HANDOFF-TRACKING.md to see what Walmart Copilot implemented. 
Test the changes and report results in the handoff log.
```
