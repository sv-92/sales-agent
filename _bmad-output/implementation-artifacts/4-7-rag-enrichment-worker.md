---
story_id: "4.7"
epic: "Epic 4: Workflow Orchestration"
title: "Enrich lead via RAG"
status: "ready-for-dev"
created: 2026-08-10
updated: 2026-08-10
---

# Story 4.7: Enrich lead via RAG

## User Story
**As a** demo user  
**I want to** enrich a lead with sales context  
**So that** the workflow uses product/pricing knowledge for better qualification

## Business Value
This story connects the RAG knowledge base to the workflow engine, demonstrating that automated processes can leverage the same AI-powered knowledge retrieval as the conversational agent. It shows enterprise value: workflows that augment data with contextual intelligence rather than simple database lookups. The enrichment step makes the subsequent LLM scoring more accurate by providing relevant product and pricing context.

## Acceptance Criteria
```gherkin
Given the Zeebe workflow has reached the enrichment service task
And the FAISS knowledge base contains relevant sales documents
When the enrichment worker picks up the task
Then the worker queries the RAG store with the lead's industry/context
And relevant knowledge chunks are retrieved from FAISS
And the enrichment text is added to the workflow variables
And the enrichment result is visible in workflow logs or state
And the workflow proceeds to the scoring task
```

## Technical Requirements

### Stack & Dependencies
- **Python**: 3.11+
- **pyzeebe**: Worker framework for subscribing to service tasks
- **FAISS retriever**: From Story 2.5 (RAG index)
- **LangChain**: Retriever interface

### Architecture Compliance

#### Component Structure
This story implements the **pyzeebe Workers** component — specifically the enrichment worker.

**Critical Architecture Points:**
1. **Worker Pattern**: Subscribe to `enrich_lead` task type in Zeebe
2. **RAG Integration**: Use the retriever from Story 2.5 to search knowledge base
3. **Variable Passing**: Worker reads lead data from workflow variables, writes enrichment back
4. **Decoupled**: Worker runs independently, subscribes to tasks via gRPC

#### Data Flow
```
Zeebe activates "enrich_lead" task
  → pyzeebe worker picks up job
  → Worker constructs search query from lead data (industry, company)
  → RAG retriever returns relevant chunks
  → Worker formats enrichment summary
  → Worker completes job with enrichment_text variable
  → Workflow proceeds to scoring task
```

### File Structure Requirements

**Expected New Files:**
```
salesflow_agent/
  workflows/
    workers/
      __init__.py
      enrichment_worker.py    # pyzeebe worker for lead enrichment
```

### Critical Implementation Details

#### 1. Enrichment Worker (`salesflow_agent/workflows/workers/enrichment_worker.py`)
```python
# Must:
# - Subscribe to task type "enrich_lead"
# - Read lead variables: company_name, industry, context
# - Construct semantic search query from lead data
# - Call FAISS retriever with query
# - Format top-3 chunks into enrichment summary
# - Return enrichment_text as workflow variable
# - Handle retriever failures gracefully (return "no enrichment available")
# - Log enrichment results for demo visibility
```

### Testing Requirements

**Acceptance Test Scenarios:**
1. **Happy Path**: Worker enriches lead with relevant knowledge
2. **No Results**: Worker handles empty retriever results gracefully
3. **Variable Passing**: Enrichment text appears in workflow variables after completion
4. **Task Completion**: Worker marks job as complete in Zeebe

### Dependencies
- **Upstream**: Story 2.5 (FAISS index and retriever), Story 4.6 (Zeebe workflow)
- **Downstream**: Story 4.8 (Scoring Worker uses enrichment_text)

### Known Constraints
- **RAG Required**: FAISS index must be built before worker can function
- **Docker Required**: Zeebe must be running for worker to subscribe
- **Simple Enrichment**: Just retrieve and concatenate — no complex reasoning at this stage
