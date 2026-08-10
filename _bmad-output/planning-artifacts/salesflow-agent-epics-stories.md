# Epics and Stories: SalesFlow Agent

## Epics

### Epic 1: Agent Core and Conversational Pipeline
- Build the FastAPI service and conversational endpoint.
- Implement a LangChain ReACT agent using Claude.
- Integrate the agent with MCP tool discovery and invocation.
- Support demo queries like top deals by value and forecast by quarter.

### Epic 2: RAG Knowledge Base
- Create a small sales knowledge corpus with playbooks, pricing guides, and objection handling.
- Build embedding and FAISS index creation.
- Add a retriever interface for the agent and workflow workers.
- Ensure the agent can ground responses using retrieved documents.

### Epic 3: MCP CRM Discovery
- Build a FastMCP server over SQLite demo CRM data.
- Define discoverable tools for deals, accounts, contacts, forecasts, and leads.
- Add runtime agent discovery of MCP tools.
- Validate CRM data retrieval from the agent.

### Epic 4: Workflow Orchestration
- Define a BPMN lead qualification workflow for Zeebe.
- Implement pyzeebe workers for enrichment and scoring tasks.
- Wire the workflow to the FastAPI app for lead submission.
- Surface workflow outcomes in demo logs or API responses.

### Epic 5: Local Developer Experience
- Add `docker-compose.yml` for Zeebe/Camunda.
- Add startup docs and run instructions.
- Add seeded data fixtures and environment variable configuration.
- Keep the prototype runnable with minimal commands.

## Stories

### Story 1: Conversational pipeline query
- As a demo user, I can ask the agent "What are my top 5 deals by value?" so I can see the highest-value pipeline opportunities.
- Acceptance:
  - The agent returns a ranked list of at least 3 deals.
  - The list includes deal name, amount, and stage.
  - The response is produced by calling a discovered MCP CRM tool.

### Story 2: Forecast question via MCP
- As a demo user, I can ask "What's the forecast for Q3?" so I can see sales projection data from the mock CRM.
- Acceptance:
  - The agent calls the MCP forecast tool.
  - The answer includes a forecast number or summary for Q3.

### Story 3: Objection handling guidance
- As a sales rep, I can ask "How should I handle a pricing objection from an enterprise customer?" so I can get grounded sales advice.
- Acceptance:
  - The agent retrieves relevant RAG documents.
  - The response includes at least one concrete recommendation.
  - The answer references pricing or objection-handling guidance.

### Story 4: Discover MCP tools dynamically
- As a developer, I can start the app and see MCP CRM tools discovered at runtime so I can add new sources without code changes.
- Acceptance:
  - The agent logs or exposes tool metadata from FastMCP discovery.
  - At least one tool is discovered automatically.

### Story 5: Build the sales RAG index
- As a developer, I can embed and index sales playbook documents into FAISS so the agent can search them.
- Acceptance:
  - The index stores document embeddings.
  - The retriever returns relevant chunks for a sales question.

### Story 6: Lead qualification workflow start
- As a demo user, I can submit a new lead and start a Zeebe workflow so I can observe the qualification process.
- Acceptance:
  - The workflow starts successfully.
  - The process reaches enrichment and scoring tasks.

### Story 7: Enrich lead via RAG
- As a demo user, I can enrich a lead with sales context so the workflow uses product/pricing knowledge.
- Acceptance:
  - The workflow enrichment step queries the RAG store.
  - The enrichment text is visible in workflow logs or state.

### Story 8: Score lead with LLM and route
- As a demo user, I can score a lead and route it based on confidence so I can see automated qualification decisions.
- Acceptance:
  - The workflow uses Claude to compute a fit/intent score.
  - The process branches to auto-qualified or human review.

### Story 9: Local startup experience
- As a developer, I can run `docker-compose up` and `python -m salesflow_agent` so I can start the demo locally.
- Acceptance:
  - Zeebe starts in Docker.
  - The app starts without errors.
  - The demo endpoints are reachable on the expected port.

### Story 10: Simple demo content and fixtures
- As a demo maintainer, I can load seeded CRM data and sales knowledge documents so the prototype is immediately usable.
- Acceptance:
  - SQLite is seeded with deals, accounts, contacts, and forecasts.
  - The knowledge corpus contains at least 5 relevant sales documents.
  - The demo works using the seeded content without manual data entry.

## Story Mapping Notes
- Epic 1 and Epic 3 are the highest priority for the core ReACT + MCP demo.
- Epic 2 is essential for the grounded RAG experience and should be built in parallel.
- Epic 4 is the storytelling edge that demonstrates workflow orchestration, but it can be scoped small for MVP.
- Epic 5 ensures reviewers can run the system quickly and should be completed as part of each epic.
