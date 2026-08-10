# Lead Qualification BPMN Workflow

## 📋 Overview

This BPMN diagram demonstrates a complete **AI-powered lead qualification workflow** designed for Camunda 8 / Zeebe. It showcases modern GenAI integration patterns within business process automation.

## 🎯 Purpose

This is a **demo workflow** to visualize the lead qualification process. It's designed to be opened in **Camunda Modeler** to show:
- How LLMs integrate into BPMN workflows
- Service task orchestration patterns
- AI-powered decision gateways
- Multi-stage enrichment and scoring

## 🚀 How to View

### Open in Camunda Modeler:

1. Download **Camunda Modeler**: https://camunda.com/download/modeler/
2. Open Camunda Modeler
3. File → Open → Select `lead_qualification.bpmn`
4. You'll see the complete workflow with all tasks and gateways

### Or View in VS Code:

Install the **BPMN Editor** extension:
- Search for "BPMN Editor" in VS Code extensions
- Open `lead_qualification.bpmn` to see the diagram

## 📊 Workflow Steps

### 1. **Start: New Lead Received**
Entry point when a new lead is submitted

### 2. **Validate Lead Data**
- **Type**: Service Task
- **Worker**: `validate_lead`
- **Purpose**: Check required fields (company name, industry, contact)
- **Outputs**: `validation_status`

### 3. **Gateway: Valid Lead?**
- **Type**: Exclusive Gateway
- **Decision**: Routes to CRM lookup if valid, rejects if invalid
- **Condition**: `validation_status = "valid"`

### 4. **Check CRM for Existing Account**
- **Type**: Service Task  
- **Worker**: `crm_lookup`
- **Purpose**: Search SQLite/CRM for existing account records
- **Outputs**: `existing_account`, `account_id`

### 5. **Enrich Lead with Knowledge Base** 🤖
- **Type**: Service Task
- **Worker**: `enrich_lead`
- **Purpose**: Query RAG vector store for relevant sales context
- **Data**: Product fit, pricing guidance, industry playbooks
- **Outputs**: `enrichment_text`, `relevant_products`, `pricing_guidance`

### 6. **Fetch Company Data (External API)**
- **Type**: Service Task
- **Worker**: `external_api_enrich`
- **Purpose**: Call external APIs (Clearbit, LinkedIn, etc.)
- **Outputs**: `company_size`, `annual_revenue`, `employee_count`

### 7. **Score Lead with AI (Claude)** 🧠
- **Type**: Service Task
- **Worker**: `score_lead`
- **Purpose**: LLM analyzes all data and assigns 0-100 score
- **Model**: Claude Sonnet 4
- **Scoring Criteria**:
  - Industry alignment (0-30 points)
  - Budget potential (0-30 points)
  - Product relevance (0-40 points)
- **Outputs**: `lead_score`, `score_reasoning`, `route_decision`

### 8. **Gateway: Route by Score**
- **Type**: Exclusive Gateway
- **Decision Logic**:
  - Score ≥ 70 → **Sales Path**
  - Score 40-69 → **Nurture Path**
  - Score < 40 → **Disqualified Path**

### 9a. **Assign to Sales Team** (High Score)
- **Type**: Service Task
- **Worker**: `assign_to_sales`
- **Purpose**: Assign to appropriate sales rep
- **Outputs**: `assigned_rep`, `sales_queue`

### 9b. **Add to Nurture Campaign** (Medium Score)
- **Type**: Service Task
- **Worker**: `add_to_nurture`
- **Purpose**: Add to marketing automation campaign
- **Outputs**: `campaign_id`, `nurture_stage`

### 9c. **Mark as Disqualified** (Low Score)
- **Type**: Service Task
- **Worker**: `disqualify_lead`
- **Purpose**: Archive with disqualification reason
- **Outputs**: `disqualification_reason`

### 10. **Update CRM with Results**
- **Type**: Service Task
- **Worker**: `update_crm`
- **Purpose**: Write all workflow results back to CRM database
- **Updates**: Score, route decision, assignment

### 11. **Send Notification Email**
- **Type**: Service Task
- **Worker**: `send_notification`
- **Purpose**: Notify sales rep or marketing team
- **Contains**: Lead details, score, assigned rep

### 12. **End: Lead Qualified**
Workflow completes successfully

## 🎨 Visual Elements

### Service Tasks (Blue Rectangles):
- **Validate Lead Data**
- **Check CRM**
- **Enrich Lead** (RAG/AI)
- **External API**
- **Score Lead** (LLM)
- **Assign/Nurture/Disqualify**
- **Update CRM**
- **Send Notification**

### Gateways (Diamonds):
- **Valid Lead?** - Validation check
- **Route by Score** - 3-way split based on LLM score

### Events (Circles):
- **Start**: New Lead Received
- **End**: Lead Qualified
- **End**: Lead Rejected

## 🔧 Technical Details

### Camunda 8 / Zeebe Configuration:

```xml
<zeebe:taskDefinition type="enrich_lead" />
<zeebe:ioMapping>
  <zeebe:input source="=company_name" target="company_name" />
  <zeebe:output source="=enrichment_text" target="enrichment_text" />
</zeebe:ioMapping>
```

### Worker Types Defined:
1. `validate_lead`
2. `crm_lookup`
3. `enrich_lead` ← **RAG/Vector Store**
4. `external_api_enrich`
5. `score_lead` ← **LLM/Claude**
6. `assign_to_sales`
7. `add_to_nurture`
8. `disqualify_lead`
9. `update_crm`
10. `send_notification`

### Gateway Conditions:

```xml
<!-- Validation -->
=validation_status = "valid"

<!-- High Score (Sales) -->
=lead_score >= 70

<!-- Medium Score (Nurture) -->
=lead_score >= 40 and lead_score < 70

<!-- Low Score (Disqualified) -->
=lead_score < 40
```

## 💡 Key Concepts Demonstrated

### 1. **AI-Powered Decision Making**
- LLM evaluates lead quality
- Structured output (score + reasoning)
- Replaces manual qualification

### 2. **Multi-Stage Enrichment**
- Internal data (CRM lookup)
- Knowledge base (RAG retrieval)
- External APIs (company data)

### 3. **Intelligent Routing**
- Gateway uses LLM output
- Three qualification tiers
- Automated assignment

### 4. **Process Orchestration**
- BPMN standardization
- Service task composition
- Zeebe execution

## 🎤 Demo Talking Points

When presenting this workflow to interviewers:

1. **"This workflow combines traditional BPM with modern GenAI"**
   - Classical BPMN for structure
   - AI workers for intelligence

2. **"The enrichment step queries our RAG knowledge base"**
   - Vector similarity search
   - Product/pricing context
   - Industry playbooks

3. **"Claude scores the lead holistically"**
   - Not just rules-based scoring
   - Considers enrichment context
   - Explains its reasoning

4. **"The gateway routes based on AI confidence"**
   - High score → immediate sales
   - Medium → nurture campaign
   - Low → polite decline

5. **"This is production-ready architecture"**
   - Camunda 8 enterprise-grade
   - Zeebe scales to millions of instances
   - Python workers are horizontally scalable

## 🔗 Integration Points

### Connects to SalesFlow Agent:

```python
# FastAPI endpoint triggers this workflow
@app.post("/leads/qualify")
async def qualify_lead(request: LeadRequest):
    instance_key = await workflow_client.start_lead_qualification({
        "company_name": request.company_name,
        "industry": request.industry,
        "contact_name": request.contact_name
    })
    return {"workflow_instance": instance_key}
```

### Python Workers Subscribe:

```python
from pyzeebe import ZeebeWorker

@worker.task(task_type="score_lead")
async def score_lead(company_name: str, enrichment_text: str):
    llm = ChatAnthropic(model="claude-sonnet-4")
    score = await llm.ainvoke(scoring_prompt)
    return {"lead_score": score, "route_decision": "sales"}
```

## 📁 File Structure

```
workflows/
├── bpmn/
│   ├── lead_qualification.bpmn  ← This file (open in Camunda Modeler)
│   └── README.md               ← You are here
├── client.py                   ← Zeebe client (starts workflow)
└── workers/
    ├── enrichment_worker.py    ← RAG enrichment
    └── scoring_worker.py       ← LLM scoring
```

## 🚀 Next Steps

1. **Open in Camunda Modeler** to see the visual diagram
2. **Walk through each task** to understand the flow
3. **Note the AI integration points** (enrich + score)
4. **Explain gateway logic** during interview

## 📚 Resources

- **Camunda Modeler**: https://camunda.com/download/modeler/
- **Zeebe Documentation**: https://docs.camunda.io/docs/components/zeebe/zeebe-overview/
- **BPMN 2.0 Spec**: https://www.omg.org/spec/BPMN/2.0/
- **pyzeebe**: https://github.com/camunda-community-hub/pyzeebe

---

**Created for**: Pinterest GenAI Engineer Interview Demo  
**Purpose**: Showcase BPMN + AI workflow orchestration  
**Status**: Demo-ready (visual only, not executable without Zeebe setup)
