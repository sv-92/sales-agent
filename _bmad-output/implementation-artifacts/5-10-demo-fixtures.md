---
story_id: "5.10"
epic: "Epic 5: Local Developer Experience"
title: "Simple demo content and fixtures"
status: "ready-for-dev"
created: 2026-08-10
updated: 2026-08-10
---

# Story 5.10: Simple demo content and fixtures

## User Story
**As a** demo maintainer  
**I want to** load seeded CRM data and sales knowledge documents  
**So that** the prototype is immediately usable without manual data entry

## Business Value
This story ensures the demo "just works" with realistic, pre-loaded data. The seeded content makes the demo compelling by showing realistic sales scenarios rather than placeholder data. It demonstrates attention to detail and user experience — critical for an interview demo.

## Acceptance Criteria
```gherkin
Given the application is starting
When the database is empty or missing
Then SQLite is seeded with deals, accounts, contacts, and forecasts
And the seed data includes realistic company names and amounts
And the knowledge corpus contains at least 5 relevant sales documents

Given the demo is running with seeded content
When the user asks "What are my top deals?"
Then realistic deal data is returned (not placeholder values)
When the user asks "How do I handle pricing objections?"
Then grounded advice from the knowledge base is returned
When the user submits "Qualify lead: Acme Corp"
Then the workflow has realistic context to work with
```

## Technical Requirements

### Stack & Dependencies
- **SQLite**: Seed script for CRM data
- **Markdown**: Knowledge corpus documents
- **Python**: Seed script executable on startup if DB missing

### File Structure Requirements

**Expected New/Updated Files:**
```
data/
  seed_data.sql               # Complete SQL seed script
  crm.db                      # Generated SQLite database (gitignored)
  knowledge/
    objection_handling.md     # Pricing and competitor objections
    discovery_questions.md    # Qualifying questions framework
    negotiation_tactics.md    # Closing and negotiation strategies
    product_positioning.md    # Value proposition messaging
    enterprise_selling.md    # Enterprise sales methodology
    account_planning.md       # Territory and account planning
```

### Critical Implementation Details

#### 1. Seed Data (`data/seed_data.sql`)
```sql
-- Must include tables:
-- deals: id, name, amount, stage, account_id, close_date, created_at
-- accounts: id, name, industry, size, revenue
-- contacts: id, name, title, email, account_id
-- forecasts: id, quarter, amount, category, confidence
-- leads: id, company_name, contact_name, industry, size, status, score

-- Must include at least:
-- 8-10 deals across different stages
-- 5 accounts (varying industries: tech, healthcare, finance, retail, manufacturing)
-- 8 contacts across accounts
-- 4 quarterly forecasts (Q1-Q4)
-- 3 leads in different qualification states
```

#### 2. Knowledge Documents (each 400-800 words)
```markdown
# Each document covers a specific sales domain:
# - Use realistic enterprise sales language
# - Include actionable tactics and frameworks
# - Structure with headers, bullets, and examples
# - Content that embeds well for semantic search
```

### Testing Requirements

1. **Fresh Start**: Delete crm.db, restart app, verify data seeded
2. **Idempotent**: Running seed twice doesn't duplicate data
3. **Data Quality**: Amounts are realistic ($10K-$1.2M range)
4. **Knowledge Coverage**: Each user journey has supporting documents

### Dependencies
- **Upstream**: Story 1.1 (SQLite schema for deals), Story 2.5 (knowledge directory structure)
- **Downstream**: None (terminal story)

### Known Constraints
- **Realistic but Fictional**: Use plausible company names, not real companies
- **Consistent Data**: Accounts referenced in deals must exist in accounts table
- **Demo-Ready**: Data should tell a coherent story (e.g., pipeline shows healthy mix of stages)
