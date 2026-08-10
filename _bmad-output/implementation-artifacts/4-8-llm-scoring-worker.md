---
story_id: "4.8"
epic: "Epic 4: Workflow Orchestration"
title: "Score lead with LLM and route"
status: "ready-for-dev"
created: 2026-08-10
updated: 2026-08-10
---

# Story 4.8: Score lead with LLM and route

## User Story
**As a** demo user  
**I want to** score a lead and route it based on confidence  
**So that** I can see automated qualification decisions powered by LLM reasoning

## Business Value
This story demonstrates the most compelling GenAI workflow pattern: an LLM making structured business decisions within an automated process. The scoring worker uses Claude to evaluate lead fit/intent based on enriched context, then the workflow routes based on the score. This shows how GenAI transforms traditional rule-based workflows into intelligent, context-aware automation.

## Acceptance Criteria
```gherkin
Given the Zeebe workflow has reached the scoring service task
And the workflow variables include lead data and enrichment_text
When the scoring worker picks up the task
Then the worker uses Claude to compute a fit/intent score (0-100)
And the score includes a brief reasoning explanation
And the workflow branches based on score:
  - score >= 70: auto-qualified (routed to Sales)
  - score 40-69: human-review (routed to Nurture)
  - score < 40: disqualified
And the routing decision is visible in logs or API response
```

## Technical Requirements

### Stack & Dependencies
- **Python**: 3.11+
- **pyzeebe**: Worker framework for subscribing to service tasks
- **langchain-anthropic**: For Claude LLM scoring call
- **Pydantic**: Structured output parsing for score response

### Architecture Compliance

#### Component Structure
This story implements the **pyzeebe Workers** component — specifically the scoring worker.

**Critical Architecture Points:**
1. **Worker Pattern**: Subscribe to `score_lead` task type in Zeebe
2. **LLM Integration**: Use Claude to evaluate lead quality
3. **Structured Output**: Parse LLM response into score + reasoning
4. **Gateway Routing**: Worker sets score variable; BPMN gateway routes based on threshold

#### Data Flow
```
Zeebe activates "score_lead" task
  → pyzeebe worker picks up job
  → Worker reads: company_name, industry, enrichment_text
  → Worker constructs scoring prompt with context
  → Claude evaluates lead (fit score 0-100 + reasoning)
  → Worker parses structured response
  → Worker completes job with: score, reasoning, route
  → BPMN gateway uses score to determine path
  → Workflow ends at qualified/nurture/disqualified end event
```

### File Structure Requirements

**Expected New Files:**
```
salesflow_agent/
  workflows/
    workers/
      scoring_worker.py       # pyzeebe worker for LLM lead scoring
```

### Critical Implementation Details

#### 1. Scoring Worker (`salesflow_agent/workflows/workers/scoring_worker.py`)
```python
# Must:
# - Subscribe to task type "score_lead"
# - Read workflow variables: company_name, industry, enrichment_text
# - Construct scoring prompt:
#   "Given this lead and enrichment context, score 0-100 for sales fit.
#    Consider: industry alignment, company size, product relevance.
#    Return JSON: {score: int, reasoning: str, route: str}"
# - Call Claude with structured output request
# - Parse response into score, reasoning, route
# - Set workflow variables: lead_score, score_reasoning, route_decision
# - Handle LLM failures gracefully (default to human-review)
# - Log scoring decision for demo visibility
```

#### 2. Scoring Prompt Template
```python
SCORING_PROMPT = """
You are a sales lead qualification assistant. Score this lead 0-100.

Lead Information:
- Company: {company_name}
- Industry: {industry}

Enrichment Context:
{enrichment_text}

Score based on:
1. Industry alignment with our product (0-30 points)
2. Company size and budget potential (0-30 points)
3. Product relevance from enrichment (0-40 points)

Respond in JSON format:
{{"score": <0-100>, "reasoning": "<brief explanation>", "route": "<sales|nurture|disqualified>"}}

Route rules: score >= 70 → "sales", 40-69 → "nurture", < 40 → "disqualified"
"""
```

### Testing Requirements

**Acceptance Test Scenarios:**
1. **High Score Lead**: Enterprise tech company scores 70+, routes to Sales
2. **Low Score Lead**: Irrelevant industry scores < 40, routes to Disqualified
3. **Mid Score Lead**: Partial fit scores 40-69, routes to Nurture
4. **LLM Failure**: Worker handles API errors gracefully (defaults to human-review)
5. **Structured Output**: Score response is parseable JSON with required fields

### Dependencies
- **Upstream**: Story 4.6 (Zeebe workflow), Story 4.7 (Enrichment Worker provides enrichment_text)
- **Downstream**: None (terminal workflow step)

### Known Constraints
- **LLM Cost**: Each scoring call uses ~500 tokens — budget-safe for demo
- **Docker Required**: Zeebe must be running
- **Prompt Engineering**: Keep prompt simple and deterministic for demo reliability
- **No Retry Logic**: Single LLM call per lead (demo scope)
