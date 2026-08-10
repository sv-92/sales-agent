# Interview Preparation Context — Pinterest GenAI Engineer Role

> **Purpose**: This document contains all the context from my resume preparation and interview prep sessions. Use this to help me with interview preparation, project building, and recalling technical details from my work experience. I have been working with an AI assistant on my work laptop that has access to my actual Walmart repos — this document captures the key architecture and design patterns from those repos that I cannot share directly.

---

## IMMEDIATE GOAL

I have a **45-minute hiring manager interview** with **Peter** at Pinterest for a **GenAI Engineer** position on the IT Enterprise Systems team (Sales/Marketing/Finance focus).

**What Peter cares about** (insider intel from my referral who reports directly to him):
- Self-driven engineers who talk to product/business, understand problems, create solutions, deliver fast
- MCP (Model Context Protocol)
- RAG (Retrieval Augmented Generation)
- Agent building
- He comes from an engineering background but isn't deeply technical — more interested in how you work than implementation minutiae

**Secondary goal**: Build a lightweight prototype project (Python + Zeebe + RAG + MCP + LLM) to:
1. Brush up on these technologies hands-on
2. Have something concrete to reference/demo if asked
3. Practice spec-driven development using BMad framework

---

## TARGET ROLE DETAILS

**Company**: Pinterest
**Team**: IT Enterprise Systems (Sales/Marketing/Finance)
**Title**: GenAI Engineer
**Level**: Staff / Senior Staff (10+ YOE required)

**Key JD Requirements**:
- GenAI/ML-powered services at scale
- LLM-based workflows and agentic patterns
- Evaluation frameworks for LLM quality
- Observability and validation guardrails
- Event-driven architectures and distributed systems
- AI coding tools (building AND evaluating them)
- Python primary language
- Salesforce is a plus
- Sales/Marketing/Finance enterprise systems focus

---

## MY PROFESSIONAL SUMMARY

Staff Software Engineer with 10+ years of full-stack experience and 3+ years leading production GenAI/ML systems at enterprise scale at Walmart Global Tech. Architected LLM-powered agentic workflows, ReACT agents, and BPMN-orchestrated automation serving 2,000+ business users and unlocking $500M+ in revenue impact (referenced in company earnings call). Built end-to-end AI services with custom evaluation frameworks, observability, and validation guardrails.

---

## PROJECT DEEP DIVES (From Walmart Repos)

### Project 1: Wally — AI-Powered Enterprise Data Agent (Savant Repo)

**What it is**: Production ReACT agent providing natural language data analysis to Sales, Merchandising, and Finance teams. 2,000+ users across US and International business units.

**Architecture**:
```
Merchant Question (Natural Language)
    ↓
FastAPI Endpoint → JWT Auth → Tenant Resolution
    ↓
ReACT Agent (LangChain + Azure OpenAI GPT-4.1)
    ↓ (Iterative Thought → Action → Observation loop)
Tool Selection (40+ domain-specific tools)
    ├── Semantic Query Tools → Cube.js Semantic Layer → BigQuery
    ├── Knowledge Base Tool → Milvus Vector DB (RAG)
    ├── MCP External Tools → Dynamic discovery from MCP servers
    ├── Memory Tools → Episodic Memory Service (PostgreSQL)
    ├── Store/Item/Supplier Tools → Internal APIs
    └── Utility Tools (date parsing, user profile, etc.)
    ↓
LLM Response Synthesis
    ↓
Streaming Response to Merchant UI
```

**RAG Implementation (REAL — from my code)**:
- **Vector DB**: Milvus cluster (gRPC connection with auth)
- **Embeddings**: Azure OpenAI `text-embedding-ada-002` via Walmart's embedding service (RSA-signed auth headers)
- **Retrieval**: `MilvusService.fetch_relevant_chunks()` — async similarity search with relevance scores, returns top-k=4 results above configurable score threshold
- **Knowledge Base**: Merchant documentation (product sourcing, category management, pricing strategy, inventory management, vendor relations)
- **Resilience**: Tenacity retry with exponential backoff (3 attempts), connection pooling, automatic reconnection on gRPC failures
- **Integration**: Exposed as `search_merchant_knowledge_base` tool — agent autonomously decides when to query knowledge base based on user question

**MCP Implementation (REAL — from my code)**:
- **Library**: FastMCP (v2.14.0)
- **Multi-Tenant Config**: Per-tenant MCP server endpoints bootstrapped at app startup
- **Authentication**: RSA-signed headers (consumer ID + timestamp + key version)
- **McpToolWrapper**: Custom LangChain BaseTool wrapper that makes any MCP tool look like a native agent tool
- **Dynamic Discovery**: `get_mcp_external_tools()` reads tool specs (name, inputSchema, description, fallback, is_offline) from MCP servers and registers them dynamically
- **BQ Audit MCP Server**: Built an MCP server exposing BigQuery data with 5 tools (query_tickets, count_tickets, check_product_status, query_products, get_vendor_products)
- **Extensibility**: Adding new data sources = spin up MCP server, agent auto-discovers tools

**Tool System (40+ tools)**:
- Semantic Query (natural language → SQL via Cube.js)
- Business Summary, Sales Budget Forecast, Price Gap Analysis, Market Share
- Store Item, Store Traits, Supplier Profile, Product Search
- Knowledge Base (RAG), Memory Search/Add, User Profile
- CVP Ecomm, IMU Impact, PDP Lookup

**Multi-Tenant Design**:
- Tenant groups (tg1=US, tg2=International)
- Per-tenant: agents, tools, secrets, MCP configs, prompts
- Dynamic agent loading via `get_agent.py`

**Key Patterns**:
- ReACT reasoning loop (Thought → Action → Observation → repeat)
- Autonomous tool selection via LLM
- Parallel tool execution for independent operations
- Episodic memory for conversation context
- Streaming responses for UX
- Token-based auth (JWT) with role claims

**Tech Stack**: Python, FastAPI, LangChain 0.3.27, Azure OpenAI (GPT-4.1, GPT-4-turbo), Milvus (PyMilvus 2.5.10), Pydantic 2.11, SQLAlchemy 2.0, FastMCP, OpenTelemetry, Arize Phoenix

---

### Project 2: Assortment Gap Agent (AGA-TXA Repo)

**What it is**: Autonomous execution agent for merchandising workflow automation. Processes millions of items across 6+ workflow types, contributing to $500M+ in unlocked inventory value. Cited in Walmart earnings call.

**Architecture**:
```
BigQuery (Item Data Source)
    ↓
Zeebe BPMN Workflow (Camunda 8)
    ├── Fetch Worker → Queries BigQuery with chunking (LIMIT/OFFSET)
    ├── Multi-Instance Parallel → Each chunk processed concurrently
    │   ├── Orderability Updates (STORE_ONLY → ONLINE_AND_STORE)
    │   ├── Transactability Fixes (offer type, site end dates)
    │   ├── Missing Image Remediation (supplier API → image update)
    │   └── Replenishment Activation
    ├── Item Intake API → Submit changes
    ├── Audit Worker → BigQuery logging
    └── Loop until has_more_chunks=False
```

**Workflow Types**:
1. **Orderability** — Fix items that can't be ordered online
2. **Transactability (Offer Type)** — Update offer types for marketplace items
3. **Transactability (Site End Date)** — Fix expiration dates
4. **Missing Images** — Retrieve and submit missing product images
5. **Replenishment** — Activate replenishment for items
6. **3P-to-1P Conversion** — Convert marketplace SKUs to first-party (involves Salesforce CMDA)

**Zeebe/BPMN Patterns**:
- **gRPC with OAuth token refresh** — Custom `RefreshingOAuthCredentials` for Zeebe cluster auth
- **Multi-tenant**: `wmt_merchandising_us` tenant
- **Database Chunking**: SQL pagination → BPMN multi-instance → parallel per-item processing → bounded memory
- **Graceful Shutdown**: `shutdown_event`, 70s timeout, running job tracking
- **Worker Specialization**: `ZEEBE_WORKER_NAME` env var for horizontal scaling specific workers
- **Task Router Pattern**: `ZeebeTaskRouter` with decorated task handlers
- **Dry-Run Mode**: Simulates without side effects for testing

**Salesforce Integration**:
- Sales Cloud for vendor/partner master data (CMDA)
- During 3P-to-1P conversions: validate supplier eligibility, contract terms, compliance status
- Automates outreach workflows

**Key Design Decisions**:
- Chunking at Zeebe level (not app level) for scalability to 10K+ items
- Multi-instance parallelism with bounded concurrency (`max_running_jobs`)
- Deterministic business logic (no LLM needed for rule-based fixes)
- Comprehensive error handling with `failed_items`, `conflicted_items` tracking

**Tech Stack**: Python, FastAPI, pyzeebe 4.5.0, gRPC, BigQuery, SQLAlchemy 2.0 (async), asyncpg, Pydantic, OpenTelemetry, Prometheus, httpx

---

### Project 3: Store Ticket Agent (merch-store-ticket-agents Repo)

**What it is**: End-to-end automated ticket resolution system processing 1M+ annual tickets from hundreds of US stores. Uses LLM for classification and decision-making.

**Architecture**:
```
Ticket Sources (OSC / ServiceNow / Salesforce Service Cloud)
    ↓
OAuth-authenticated REST API ingestion
    ↓
Hybrid Classification (Regex fast-path → LLM fallback)
    ↓
[Split by Type]
    ├── Markdown Requests → Category Flow → Store Item Flow
    ├── NOF (Not On File) → UPC validation → Image processing
    ├── Overstock → Item validation → Resolution
    └── Understock → LangGraph Decision Graphs → Analysis
    ↓
[Per-Item Processing — BPMN Multi-Instance]
    ├── Parallel data retrieval (IQS, BigQuery, GCS)
    ├── LLM Summarization & Judgment
    ├── Rule-based decision engine + LLM guardrails
    └── Human-in-the-loop Action Center (edge cases)
    ↓
[Resolution]
    ├── Auto-resolve (60% of tickets)
    ├── Create MD Plan via OSC API
    ├── Email merchant for approval
    └── Forward to CC (non-compatible)
    ↓
BigQuery Audit Logging
```

**LLM Integration Points**:
1. **Classification**: Determine ticket type (markdown, NOF, overstock, understock) — 95%+ accuracy
2. **Extraction**: Parse unstructured ticket text into structured data
3. **Judgment**: Validate classification correctness
4. **Summarization**: Generate merchant-friendly explanations
5. **Decision (LangGraph)**: Stateful decision graphs for root cause analysis across ticket types

**LangGraph Usage**:
- Stateful decision graphs for understock analysis
- Tracks `langraph_code_decision` (approve/deny/escalate) and `langraph_analysis_path` (JSON trace)
- Multiple decision factors weighed through graph traversal

**Hybrid Classification Strategy**:
```
1. Try regex parsing (fast, pattern-based, ~0ms)
2. If regex matches → extract data directly (no LLM cost)
3. If no match → use LLM for classification (GPT-4)
4. Confidence threshold check → low confidence → forward to human
```

**Integration Layer**:
- **OSC (Oracle Service Cloud)**: OAuth token management with auto-refresh, ticket status transitions, queue management, 100+ dept-to-product mappings
- **ServiceNow**: Ticket intake source
- **IQS (Item Query Service)**: Product catalog data (descriptions, attributes, pricing)
- **BigQuery**: Historical markdown data, item metrics, audit logging
- **GCS**: Report storage and data exchange

**Human-in-the-Loop Action Center**:
- ~10% of tickets escalated for merchant review
- AI-generated recommendations presented with confidence scores
- Merchant approves/rejects/modifies
- Feedback loop for model improvement

**BMad Framework Integration**:
- Spec-driven development — AI agents generate design docs, specs, test plans before implementation
- Technical design documents validated by AI before coding begins
- Integrated into team's SDLC

**Key Metrics**:
- 95%+ classification accuracy
- 60% auto-resolution rate
- 40% reduction in average resolution time
- 1M+ tickets processed annually

**Tech Stack**: Python, FastAPI, pyzeebe, LangChain, LangGraph, Azure OpenAI (GPT-4), SQLAlchemy 2.0 (async), BigQuery, Pydantic, OpenTelemetry

---

### Project 4: Proctor — LLM Evaluation Platform

**What it is**: Custom black-box evaluation framework for compound AI systems. Validates LLM outputs against golden datasets using multiple scoring strategies.

**Architecture**:
```
Golden Dataset (JSON test cases)
    ↓
Solver (calls agent under test — e.g., Savant HTTP API)
    ↓
Scorer (LLM-based grading, regex extraction, custom metrics)
    ↓
Results (accuracy %, precision/recall, per-category breakdown)
```

**Evaluation Types**:
1. **Semantic Query Task** — Validates generated queries match expected structure
2. **Measures Recall Task** — Extracts metrics from responses, compares to expected set
3. **Canned Response Task** — Classifies response type (canned vs dynamic)
4. **Response Type Scoring** — Format compliance validation

**Built with Inspect AI** — Automated LLM benchmarking framework

**Why this matters for Pinterest**: JD explicitly calls out "evaluation frameworks" — this is a direct differentiator.

---

### Project 5: Semantic Layer (savant-semantic-layer Repo)

**What it is**: Cube.js semantic abstraction over 23+ BigQuery data models (financial, inventory, market share, pricing, store metrics).

**Architecture**:
```
Wally Agent (semantic_query_tool)
    ↓
Cube.js Server (GraphQL API)
    ↓
BigQuery Data Warehouse (wmt-edw-prod)
```

**Key Design**:
- Business users query in natural language
- Cube.js translates to optimized BigQuery SQL
- Multi-tenant BigQuery schema selection
- OMNI hierarchy integration (dept → category → subcategory → product)
- OpenTelemetry tracing for Phoenix observability

---

### Project 6: Merchandising Analytics Platform (ws-merchone-vizdis Repo)

**What it is**: Java/Spring Boot APIs and dashboards serving financial KPIs for 400M+ products.

**Key Points**:
- REST APIs: GMV, YOY performance, revenue opportunities
- Custom Rules engine (Kotlin)
- Migrated Salesforce Apex batch jobs to GCP Spark (eliminated governor limit violations)
- Hierarchical data levels (company → division → department → category)

---

## CROSS-CUTTING ARCHITECTURE PATTERNS (Interview Talking Points)

### 1. ReACT Agent Pattern
- Thought → Action → Observation loop
- Autonomous tool selection (40+ tools)
- LLM decides WHICH tool to call and HOW
- Parallel execution for independent operations
- Used in: Wally (Savant)

### 2. BPMN/Zeebe Workflow Orchestration
- Visual, standardized business process modeling
- Multi-instance parallel processing (bounded concurrency)
- Fault-tolerant with configurable retries
- Database chunking for large-scale batch operations
- Multi-tenant support
- Used in: Store Ticket Agent, AGA-TXA

### 3. RAG (Retrieval Augmented Generation)
- Embed documents → Store in vector DB (Milvus) → Query with semantic similarity
- Score threshold filtering (relevance cutoff)
- Top-k retrieval with LLM synthesis
- Retry with exponential backoff for resilience
- Used in: Wally (merchant knowledge base)

### 4. MCP (Model Context Protocol)
- External tool discovery without modifying agent code
- Schema-based registration (name, inputSchema, description)
- Multi-tenant MCP configs with signed auth
- Extensibility: new data source = new MCP server
- Used in: Wally (BQ Audit MCP, external tools)

### 5. Hybrid Classification (Regex + LLM)
- Fast path: regex patterns for known formats (~0ms, no cost)
- Fallback: LLM classification for unknown patterns
- Confidence thresholds for human escalation
- Cost optimization: only invoke LLM when needed
- Used in: Store Ticket Agent

### 6. LangGraph Stateful Decision Graphs
- Multi-step decision-making with state tracking
- Graph traversal records analysis path (explainability)
- Final decisions: approve/deny/escalate
- Used in: Store Ticket Agent (understock analysis)

### 7. Evaluation Frameworks
- Golden dataset approach (input + expected output)
- Solver-Scorer pattern (modular, composable)
- Metrics: accuracy, precision/recall, format compliance
- Continuous validation against regressions
- Used in: Proctor (Inspect AI)

### 8. Multi-Tenant Design
- Per-tenant: agents, tools, secrets, MCP configs, DB schemas
- Dynamic loading at startup
- Shared codebase with isolated data
- Used in: All projects

### 9. Human-in-the-Loop
- AI handles confident decisions autonomously
- Edge cases escalated with AI recommendations
- Merchant review with approve/reject/modify
- Feedback loop for model improvement
- Used in: Store Ticket Agent (Action Center), AGA (merchant review)

---

## INTERVIEW STRATEGY FOR PETER

### Opening Pitch (60 seconds)
> "At Walmart I've spent 3 years building production AI systems, but what I'm most proud of isn't the tech — it's how I work. I embed with product and merchandising teams, understand their actual workflow pain points, and then build agentic systems that solve them end-to-end. Our ReACT agent started because I watched merchants spending hours writing SQL. The ticket automation system started because I saw 1M+ tickets being manually processed. I don't wait for specs — I find the problem and ship the solution."

### Key Stories

**Story 1: RAG** (Merchant Knowledge Base)
> "We built a RAG pipeline using Milvus as our vector store with Azure OpenAI embeddings. The agent has a knowledge base tool that performs semantic similarity search over merchant documentation. When a merchant asks a question, we embed their query, retrieve the top-4 most relevant chunks above a confidence threshold, and the agent synthesizes the answer. We added retry logic with exponential backoff because the Milvus cluster occasionally had gRPC connectivity issues at scale."

**Story 2: MCP** (Cross-System Data Access)
> "We use MCP to give our agent extensible access to external data sources without modifying the agent's core code. We built a BQ Audit MCP server that exposes BigQuery tables as tools. On the agent side, we have a McpToolWrapper that takes any MCP tool's schema and dynamically registers it as a LangChain tool. So when we want to add a new data source, we just spin up an MCP server and the agent picks it up. The auth is handled via signed headers — consumer ID, timestamp, RSA signature."

**Story 3: Self-Driven / Business Embedded**
> "I sit in merchant review sessions. I watch how they use the tools. When I see friction, I prototype a solution in days using AI coding tools (Cursor, Claude Code), validate with the merchant, and ship. The Action Center came from watching merchants not trust full automation — so I built a human-in-the-loop review step for edge cases."

**Story 4: Shipping Fast**
> "I use AI coding tools daily — Cursor, Claude Code, Copilot — for spec-driven development. I pioneered integrating BMad framework into our SDLC where AI agents generate design docs, specs, and test plans before I write code. This means I'm shipping features in days, not weeks."

**Story 5: Evaluation Frameworks**
> "We built a custom eval platform called Proctor using Inspect AI. It's a black-box framework — we define golden datasets, create solvers that call the agent, and score outputs on semantic accuracy, measure recall, and response format. We run this continuously to catch regressions when we change prompts or add tools."

### Questions to Ask Peter
1. "What's the biggest pain point your team is dealing with right now that you'd want a new engineer to tackle first?"
2. "How does your team currently use MCP or RAG — are you building from scratch or iterating?"
3. "How do engineers on your team interact with product and business stakeholders?"
4. "What does 'shipping fast' look like on your team?"

---

## PROTOTYPE PROJECT PLAN

### Concept: SalesFlow Agent
A lightweight Python + Zeebe agent for a **sales pipeline use case** demonstrating:
- BPMN workflow orchestration (Camunda 8 / Zeebe)
- RAG (vector search over sales docs/knowledge base)
- MCP (external tool discovery — e.g., CRM data access)
- LLM for analysis, recommendations, and summarization
- Human-in-the-loop for low-confidence decisions

### Approach
1. **Use BMad** to design the project (PRD → Architecture → Epics → Stories)
2. **Keep it lightweight**: No local DB — use SQLite or BigQuery free tier, FAISS for vector (no Milvus cluster needed)
3. **Zeebe**: Use Camunda 8 SaaS free tier (or local Docker)
4. **LLM**: OpenAI API (or local Ollama for cost)
5. **MCP**: Build a simple MCP server exposing mock sales data
6. **RAG**: FAISS + OpenAI embeddings over sample sales docs

### Sales Use Case Ideas (Pinterest-relevant)
- **Lead Scoring Agent**: Ingests leads → enriches with RAG knowledge → LLM scores → workflow routes high-value leads
- **Sales Forecast Anomaly Detector**: Ingests pipeline data → detects anomalies → LLM root cause analysis → recommendations
- **CRM Health Monitor**: Checks data quality → flags issues → LLM summarizes → creates remediation tasks

### Tech Stack (Local/Lightweight)
```
Python 3.11+
FastAPI (API layer)
pyzeebe (Zeebe/BPMN orchestration)
LangChain + LangGraph (agent framework)
OpenAI or Ollama (LLM)
FAISS (local vector store for RAG)
FastMCP (MCP server + client)
SQLite or BigQuery free tier (data store)
Docker (for Zeebe local)
BMad (spec-driven development)
```

### BMad Workflow
1. Product Brief → PRD
2. Architecture Design
3. Epics & Stories
4. Sprint Planning
5. Story-by-story implementation

This gives you a demo of spec-driven development you can walk through in an interview.

---

## SKILLS MATRIX (For Quick Reference)

| Category | Technologies |
|----------|-------------|
| **Programming** | Python, Java, Kotlin, C#, JavaScript/TypeScript, SQL |
| **GenAI / LLMs** | OpenAI GPT-4, Azure OpenAI, LangChain, LangGraph, Instructor, Prompt Engineering, ReACT Agents, Tool Calling, MCP |
| **ML/AI Patterns** | RAG, Agentic Workflows, LLM Classification, Decision Graphs, Semantic Layers, Evaluation Frameworks |
| **Frameworks** | FastAPI, LangChain, LangGraph, Pydantic, SQLAlchemy (async), .NET Core, Spring Boot, Cube.js |
| **Orchestration** | Camunda 8/Zeebe (BPMN), Event-Driven Architecture, Multi-Instance Parallel Processing |
| **Data & Pipelines** | BigQuery, Cosmos, PostgreSQL, Aerospike, Apache Spark, Kafka, Druid, Elasticsearch, FAISS, Milvus |
| **LLMOps / Observability** | OpenTelemetry, Arize Phoenix, LangSmith, Prometheus, Splunk, Inspect AI |
| **Cloud & Infra** | GCP (BigQuery, GCS, DataProc), AWS, Kubernetes, Docker, CI/CD |
| **CRM / Enterprise** | Salesforce (Sales Cloud, Apex, Workflows), ServiceNow, OSC |
| **AI Dev Tools** | Cursor, Claude Code, GitHub Copilot, Windsurf, Gemini, BMad |

---

## RECRUITER CALL NOTES

- Recruiter call went well, led to this hiring manager round
- Position confirmed: GenAI Engineer on IT Enterprise Systems team
- Team focuses on Sales, Marketing, and Finance internal tools
- Referral is on the same team, reports to Peter

---

## KEY NUMBERS TO REMEMBER

- 2,000+ users (Wally agent)
- $500M+ unlocked inventory value (AGA)
- 1M+ tickets/year (Store Ticket Agent)
- 95%+ classification accuracy
- 60% auto-resolution rate
- 40% resolution time reduction
- 23+ BigQuery data models (Semantic Layer)
- 40+ agent tools (Wally)
- 6+ workflow types (AGA)
- 4+ product teams consuming shared library
- 10+ years total experience, 3+ years GenAI
- 8-10 engineers mentored on GenAI patterns
