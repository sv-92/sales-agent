---
story_id: "2.5"
epic: "Epic 2: RAG Knowledge Base"
title: "Build the sales RAG index"
status: "ready-for-dev"
created: 2026-08-10
updated: 2026-08-10
---

# Story 2.5: Build the sales RAG index

## User Story
**As a** developer  
**I want to** embed and index sales playbook documents into FAISS  
**So that** the agent can search them for grounded responses

## Business Value
This story provides the foundational RAG infrastructure that Story 2.3 (Objection Handling) depends on. Without an embedding index, the agent cannot retrieve relevant sales knowledge. This story creates the document corpus, generates embeddings, and builds a FAISS vector store that supports semantic search. It validates the RAG architecture pattern and enables all knowledge-grounded agent responses.

## Acceptance Criteria
```gherkin
Given a set of sales playbook markdown documents exist in the knowledge directory
When the embedding index builder runs
Then document embeddings are generated using a text embedding model
And the embeddings are stored in a FAISS index file on disk
And the retriever returns relevant chunks for a sample sales question
And the index supports at least 5 source documents
And the index can be rebuilt from source documents without manual steps
```

## Technical Requirements

### Stack & Dependencies
- **Python**: 3.11+
- **FAISS**: `faiss-cpu>=1.9.0` for local vector search
- **LangChain Community**: `langchain-community` for FAISS vector store wrapper
- **Embeddings**: `langchain-anthropic` or `langchain-openai` for `text-embedding-3-small`
- **Document Loaders**: LangChain `TextLoader` or `UnstructuredMarkdownLoader`
- **Text Splitter**: `RecursiveCharacterTextSplitter` for chunking documents
- **Environment**: Embedding API key in `.env` (reuse ANTHROPIC_API_KEY or add OPENAI_API_KEY)

### Architecture Compliance

#### Component Structure
This story implements the **RAG / FAISS Knowledge Store** component from the architecture.

**Critical Architecture Points:**
1. **Local FAISS**: No remote vector DB — FAISS index stored on disk
2. **Rebuild Support**: Index can be regenerated from source documents at startup or via script
3. **Chunk Strategy**: Documents split into overlapping chunks for better retrieval
4. **Retriever Interface**: Expose a LangChain-compatible retriever for agent and workflow workers

#### Data Flow
```
Source Documents (markdown) → Text Splitter (chunks)
  → Embedding Model (vectors)
  → FAISS Index (stored on disk)
  → Retriever Interface (for agent/workers)
```

### File Structure Requirements

**Expected New Files:**
```
salesflow_agent/
  rag/
    __init__.py
    index_builder.py          # Script to build/rebuild FAISS index
    retriever.py              # Retriever interface for agent integration
    config.py                 # RAG configuration (chunk size, overlap, k)
data/
  knowledge/
    objection_handling.md     # Playbook: handling pricing/competitor objections
    discovery_questions.md    # Playbook: qualifying questions and techniques
    negotiation_tactics.md    # Playbook: negotiation strategies
    product_positioning.md    # Playbook: value propositions and positioning
    enterprise_selling.md     # Playbook: enterprise sales methodology
  faiss_index/                # Generated FAISS index files (gitignored)
    index.faiss
    index.pkl
```

### Critical Implementation Details

#### 1. Index Builder (`salesflow_agent/rag/index_builder.py`)
```python
# Must:
# - Load all markdown files from data/knowledge/ directory
# - Split documents using RecursiveCharacterTextSplitter
#   - chunk_size: 500 tokens
#   - chunk_overlap: 50 tokens
# - Generate embeddings using configured embedding model
# - Save FAISS index to data/faiss_index/
# - Support rebuild (delete and recreate)
# - Log document count and chunk count
```

#### 2. Retriever (`salesflow_agent/rag/retriever.py`)
```python
# Must:
# - Load FAISS index from disk
# - Expose as LangChain retriever (as_retriever())
# - Support configurable top_k (default 3)
# - Return Document objects with page_content and metadata
# - Handle missing index gracefully (trigger rebuild)
```

#### 3. Knowledge Documents (`data/knowledge/*.md`)
```markdown
# Each document should:
# - Be 300-800 words of realistic sales content
# - Include headers and bullet points for structure
# - Cover a specific sales topic thoroughly
# - Use natural language that embeds well
```

### Testing Requirements

**Acceptance Test Scenarios:**
1. **Index Build**: Run builder, verify FAISS files created on disk
2. **Retrieval Accuracy**: Query "pricing objection" returns objection_handling chunks
3. **Multiple Results**: Retriever returns top-3 relevant chunks
4. **Rebuild Idempotent**: Running builder twice produces same results
5. **Document Coverage**: All 5+ knowledge documents are indexed

### Dependencies
- **Upstream**: None (standalone RAG infrastructure)
- **Downstream**: Story 2.3 (Objection Handling) uses this retriever; Story 4.7 (RAG Enrichment Worker) uses this retriever

### Known Constraints
- **Embedding Cost**: Use cheapest embedding model available (text-embedding-3-small at $0.02/1M tokens)
- **Document Size**: Keep corpus small (5-10 docs) to minimize embedding costs
- **No Persistence Across Runs**: Index rebuilt from source if missing (acceptable for demo)
- **Chunk Size**: 500 tokens balances retrieval precision vs context window usage
