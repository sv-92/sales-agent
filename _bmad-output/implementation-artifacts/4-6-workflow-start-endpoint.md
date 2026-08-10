---
story_id: "4.6"
epic: "Epic 4: Workflow Orchestration"
title: "Lead qualification workflow start"
status: "ready-for-dev"
created: 2026-08-10
updated: 2026-08-10
---

# Story 4.6: Lead qualification workflow start

## User Story
**As a** demo user  
**I want to** submit a new lead and start a Zeebe workflow  
**So that** I can observe the qualification process

## Business Value
This story delivers the workflow orchestration entry point, demonstrating BPMN process automation triggered from the conversational agent. It validates the Zeebe integration pattern: user intent → API call → workflow instance creation → service task execution. This is the key differentiator showing enterprise-grade process orchestration integrated with GenAI.

## Acceptance Criteria
```gherkin
Given the Zeebe engine is running in Docker
And the lead qualification BPMN process is deployed
And the FastAPI application is running
When the user submits a lead (e.g., "Qualify this lead: Acme Corp")
Then a Zeebe workflow instance is created
And the process reaches the enrichment service task
And the process reaches the scoring service task
And the workflow state is visible in logs or API response
And the user receives confirmation that qualification started
```

## Technical Requirements

### Stack & Dependencies
- **Python**: 3.11+
- **pyzeebe**: `>=4.5.0` for Zeebe client and worker framework
- **Zeebe**: Runs in Docker via `docker-compose.yml`
- **BPMN**: Lead qualification process definition (XML)
- **FastAPI**: Extend existing app with workflow endpoint
- **Pydantic**: Lead submission request model

### Architecture Compliance

#### Component Structure
This story implements the **Zeebe / Camunda Workflow Engine** integration and the workflow start capability.

**Critical Architecture Points:**
1. **Docker Zeebe**: Engine runs in Docker, Python connects via gRPC
2. **BPMN Process**: Define a simple lead qualification workflow with 2-3 service tasks
3. **pyzeebe Client**: Use pyzeebe to deploy process and create instances
4. **Agent Integration**: The ReACT agent can trigger workflow via tool

#### Data Flow
```
User: "Qualify lead: Acme Corp"
  → ReACT Agent recognizes workflow intent
  → Agent calls start_qualification tool
  → pyzeebe creates workflow instance in Zeebe
  → Zeebe activates enrichment service task
  → Zeebe activates scoring service task
  → Result returned to user
```

### File Structure Requirements

**Expected New Files:**
```
salesflow_agent/
  workflows/
    __init__.py
    client.py                 # pyzeebe client setup and workflow operations
    models.py                 # Lead and workflow Pydantic models
    bpmn/
      lead_qualification.bpmn # BPMN process definition
docker-compose.yml            # Zeebe + Operate (optional) containers
```

### Critical Implementation Details

#### 1. Zeebe Client (`salesflow_agent/workflows/client.py`)
```python
# Must:
# - Create ZeebeClient connected to localhost:26500
# - Deploy BPMN process on startup
# - Expose start_lead_qualification(lead_data) function
# - Return workflow instance key for tracking
# - Handle connection errors gracefully
```

#### 2. BPMN Process (`salesflow_agent/workflows/bpmn/lead_qualification.bpmn`)
```xml
<!-- Must define:
  - Start Event: lead submitted
  - Service Task 1: "enrich-lead" (type: enrich_lead)
  - Service Task 2: "score-lead" (type: score_lead)
  - Exclusive Gateway: score >= 70 → auto-qualified, else → human-review
  - End Events: auto-qualified, human-review
-->
```

#### 3. Lead Model (`salesflow_agent/workflows/models.py`)
```python
# Must include:
# - LeadInput: company_name, contact_name, industry (optional), size (optional)
# - WorkflowResult: instance_key, status, score (optional), route (optional)
```

#### 4. Docker Compose (`docker-compose.yml`)
```yaml
# Must include:
# - Zeebe broker (camunda/zeebe:8.5.x)
# - Port mapping: 26500 (gRPC), 9600 (monitoring)
# - Simple volume for data persistence
# - Optional: Camunda Operate for visual workflow inspection
```

### Testing Requirements

**Acceptance Test Scenarios:**
1. **Workflow Starts**: Submit lead, verify workflow instance created
2. **Tasks Activate**: Verify enrichment and scoring tasks appear
3. **Connection Handling**: App starts gracefully if Zeebe is not available
4. **BPMN Deploy**: Process deploys successfully on app startup

### Dependencies
- **Upstream**: Story 1.1 (FastAPI app), Docker environment
- **Downstream**: Story 4.7 (Enrichment Worker), Story 4.8 (Scoring Worker)

### Known Constraints
- **Docker Required**: Zeebe needs Docker — this story is testable only on Personal Copilot
- **Zeebe Version**: Use 8.5.x (latest stable with pyzeebe 4.5.0 compatibility)
- **No Operate UI**: Optional — can skip Operate to reduce Docker resource usage
- **Demo Scope**: Single workflow, simple gateway logic, no timers or subprocesses
