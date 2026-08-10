---
title: SalesFlow Agent — AI-Powered Sales Pipeline Assistant
created: 2026-08-09
updated: 2026-08-09
---

# PRD: SalesFlow Agent — AI-Powered Sales Pipeline Assistant
*Working title — prototype/demo for modern GenAI engineering patterns in enterprise sales workflows.*

## 0. Document Purpose
This PRD is for the engineering team building a lightweight prototype of SalesFlow Agent. It captures the product vision, target user, glossary, core features, MVP scope, non-goals, success metrics, and implementation assumptions. The document is intended for the builder and for anyone evaluating the demo end to end.

## 1. Vision
SalesFlow Agent is a local demo application that helps sales teams answer natural language questions about pipeline data, access sales playbooks, and automate qualification workflows with an intelligent assistant. It demonstrates four modern enterprise patterns in a single prototype: ReACT tool calling, RAG-grounded knowledge retrieval, MCP discoverable data tools, and BPMN workflow orchestration.

SalesFlow Agent should feel like a practical sales assistant that can answer CRM questions, recommend objection-handling guidance, and score new leads using a workflow engine. The goal is to prove the architecture and showcase an end-to-end developer experience, not to ship production-grade enterprise software.

## 2. Target User

### 2.1 Jobs To Be Done
- As a sales engineer or prototype builder, I want a runnable demo that shows how an LLM agent can operate over CRM data, knowledge content, and workflow automation.
- As a sales rep or product reviewer, I want to ask natural language pipeline questions and get grounded, actionable answers without manually querying multiple systems.
- As a demo audience, I want to see a local setup that uses Claude, FAISS, MCP, and Zeebe together so the architecture is believable.

### 2.2 Non-Users (v1)
- Real enterprise customers expecting production-ready CRM controls, audit compliance, or secure multi-tenant deployment.
- End users needing a full SaaS product with authentication, role-based access, or large-scale data integration.

### 2.3 Key User Journeys
- **UJ-1. Sales rep queries top pipeline deals.**
  - Persona + context: A sales rep preparing for a pipeline review wants a quick view of highest-value opportunities.
  - Entry state: Local demo running, user on the conversational agent prompt.
  - Path: User asks, "What are my top 5 deals by value?" → agent discovers MCP pipeline tool → agent calls CRM tool → agent returns formatted list.
  - Climax: The user sees the top deals ranked by value and can use the summary directly.
  - Resolution: User can ask a follow-up question or export the answer for review.

- **UJ-2. Sales rep seeks objection-handling guidance.**
  - Persona + context: A rep needs support handling a pricing objection from an enterprise buyer.
  - Entry state: Demo running with RAG content loaded.
  - Path: User asks, "How should I handle a pricing objection from an enterprise customer?" → agent retrieves relevant sales playbook content via FAISS → agent synthesizes recommended guidance.
  - Climax: The user receives grounded objections handling advice citing playbook context.
  - Resolution: User feels confident to use the guidance in a real conversation.

- **UJ-3. New lead is qualified through a workflow.**
  - Persona + context: An engineer triggers the local lead qualification workflow and watches the process.
  - Entry state: Lead ingestion event is submitted to Zeebe.
  - Path: Workflow ingests the lead → RAG enriches with product/pricing context → LLM scores fit/intent → route to auto-qualified or human review queue.
  - Climax: The workflow completes and exposes a clear route decision.
  - Resolution: The team can inspect the workflow result and learn how BPMN integrates with the agent.

## 3. Glossary
- **Agent** — the conversational ReACT agent built with LangChain and Claude that reasons over tools and responds in natural language.
- **RAG** — retrieval-augmented generation where the agent uses semantic search over indexed sales knowledge before answering.
- **MCP** — Model Context Protocol, a discoverable tool protocol that exposes CRM data sources and enables dynamic agent tool discovery.
- **CRM Tool** — any MCP-discoverable endpoint that returns sales pipeline, account, contact, or forecast data.
- **FAISS** — local vector store used to index sales playbook and knowledge content for semantic retrieval.
- **Lead Qualification Workflow** — the Zeebe/BPMN process that ingests leads, enriches them, scores them, and routes them.
- **Zeebe/Camunda** — the local workflow engine running the BPMN process.
- **pyzeebe Worker** — Python worker processes that execute BPMN service tasks.
- **FastAPI** — the Python web application exposing the agent UI and HTTP APIs.

## 4. Features

### 4.1 Conversational Pipeline Assistant
**Description:** A ReACT conversational interface where a sales rep asks natural language questions and the agent uses MCP-discovered CRM tools and RAG knowledge to answer. The assistant can combine CRM queries with sales playbook context to return a single grounded response. Realizes UJ-1 and UJ-2.

**Functional Requirements:**

#### FR-1: Natural language pipeline query
- The user can ask pipeline questions in natural language and receive a response from the agent.
- Consequences:
  - The system handles at least one question about deals by pipeline value.
  - The response includes a ranked list or summary when the question requests top deals.
- Out of Scope:
  - full natural language understanding across arbitrary enterprise jargon.

#### FR-2: Grounded CRM tool invocation
- The agent can discover MCP tools and call CRM-related tools dynamically at runtime.
- Consequences:
  - The system uses MCP discovery rather than hardcoded CRM query handlers.
  - Tool calls return structured data from the mock CRM.
- Out of Scope:
  - enterprise-grade MCP service discovery across multiple real networks.

#### FR-3: Combined answer with RAG context
- When answering sales process or pricing questions, the agent retrieves relevant content from the sales knowledge base and cites it in the response.
- Consequences:
  - The system returns at least one answer grounded in retrieved playbook content.
  - The response is coherent and references context extracts where relevant.
- Notes: This feature is critical for demonstrating RAG patterns.

### 4.2 RAG Knowledge Search
**Description:** A local FAISS-backed knowledge base stores sales playbooks, pricing guides, product docs, and objection-handling content. The agent searches this store to ground answers and enrich workflow decisions. Realizes UJ-2 and UJ-3.

**Functional Requirements:**

#### FR-4: Embedding and indexing sales content
- The system can embed sales knowledge documents and store them in FAISS.
- Consequences:
  - Relevant documents return semantic similarity results for query terms.
  - The system supports local rebuild/reload of the index.

#### FR-5: Retrieval during agent response generation
- The agent retrieves top-N relevant knowledge chunks before generating answers.
- Consequences:
  - Responses include at least one knowledge snippet or paraphrase from retrieved content.
  - Retrieval latency is reasonable for a demo.
- Notes: Use Anthropic or OpenAI embeddings whichever is simpler for local demo cost control.

### 4.3 MCP-based CRM Data Discovery
**Description:** A separate FastMCP server exposes mock CRM and forecast data from SQLite. The agent discovers those tools at runtime, enabling dynamic integration with new MCP sources without code changes. Realizes UJ-1 and UJ-3.

**Functional Requirements:**

#### FR-6: FastMCP discovery of CRM tools
- The agent can query the MCP server metadata and detect available business tools.
- Consequences:
  - At least one mock CRM tool is discovered automatically.
  - The tool descriptions are visible in logs or agent tool metadata.

#### FR-7: Mock CRM data retrieval
- The agent can invoke MCP tools to get deals, accounts, contacts, and forecast information.
- Consequences:
  - The system returns structured sales data from SQLite in response to agent calls.
  - Tool calls support basic filtering (e.g., top deals by value, forecast by quarter).

### 4.4 BPMN Lead Qualification Workflow
**Description:** A Zeebe/BPMN process ingests new leads, enriches them via RAG, scores them with the LLM, and routes them to auto-qualified or human review. This demonstrates workflow orchestration integrated with AI tooling. Realizes UJ-3.

**Functional Requirements:**

#### FR-8: Lead ingestion workflow
- The system can start a BPMN lead qualification process for a submitted lead.
- Consequences:
  - Workflow starts successfully from the local environment.
  - The process reaches enrichment and scoring tasks.

#### FR-9: Enrichment via knowledge retrieval
- The workflow enriches lead data using relevant product/pricing context from the RAG store.
- Consequences:
  - The workflow stores enrichment text alongside the lead.
  - The enrichment output is visible in logs or workflow state.

#### FR-10: LLM-based scoring and routing
- The workflow scores leads using an LLM prompt and routes them based on confidence.
- Consequences:
  - High-confidence leads receive an auto-qualified outcome.
  - Low-confidence leads receive a human review route.
- Out of Scope:
  - full lead assignment or CRM synchronization.

## 5. Non-Goals (Explicit)
- Not building a production CRM app with authentication, auditing, or enterprise data governance.
- Not integrating with real Salesforce/Microsoft Dynamics or external CRM vendors.
- Not supporting multi-tenant or user-level access control.
- Not implementing full operational monitoring, alerting, or high availability.
- Not solving every natural language sales question; focus on a small set of demonstration queries.

## 6. MVP Scope

### 6.1 In Scope
- Local FastAPI app with an LLM-powered conversational agent.
- FAISS-backed RAG store with sales playbook content.
- FastMCP server exposing mock CRM data from SQLite.
- Agent discovery and dynamic invocation of discovered CRM tools.
- Local Zeebe/Camunda workflow running a lead qualification BPMN process.
- Simple local runner: `docker-compose up` for Zeebe + `python -m salesflow_agent`.

### 6.2 Out of Scope for MVP
- Production-grade security, auth, or role-based access.
- Real external CRM or enterprise system integration.
- Large-scale dataset ingestion or scalable vector store deployment.
- Human-facing UI beyond a simple conversational API or command-line prompt.
- Advanced cost optimization beyond using a low-cost Claude flow.

## 7. Success Metrics

**Primary**
- **SM-1:** Demo completes a natural language CRM query end to end. Validates FR-1, FR-2, FR-7.
- **SM-2:** Demo returns a grounded answer using RAG content for objection handling. Validates FR-3, FR-5.
- **SM-3:** Demo successfully runs a lead qualification BPMN workflow and produces a route decision. Validates FR-8, FR-10.

**Secondary**
- **SM-4:** The MCP discovery flow detects at least one CRM tool without code changes.
- **SM-5:** The local setup can be launched with `docker-compose up` and `python -m salesflow_agent`.

**Counter-metrics**
- **SM-C1:** Do not over-engineer the demo into a production platform. Counterbalances SM-5 and prevents adding unnecessary layers.

## 8. Open Questions
1. Should the prototype expose a minimal UI, or should it remain API/CLI-driven? [NOTE FOR PM]
2. Which embedding provider should be the default for the demo: Anthropic or OpenAI? Use whichever is easiest and cost-effective.
3. How many distinct MCP tool definitions are needed to convincingly demo discovery? One strong example may be sufficient.
4. Should the workflow outcome store lead decisions in SQLite or only log them? [NOTE FOR PM]

## 9. Assumptions Index
- [ASSUMPTION] The demo is local-only and is not expected to support enterprise-grade access control.
- [ASSUMPTION] A lightweight API and workflow process is enough to show the end-to-end pattern.
- [ASSUMPTION] The sales knowledge base can be represented by a small set of curated documents rather than a large enterprise corpus.
- [ASSUMPTION] Using Claude via LangChain is within the acceptable demo budget.
