---
story_id: "2.3"
epic: "Epic 2: RAG Knowledge Base"
title: "Objection handling guidance"
status: "ready-for-dev"
created: 2026-08-09
updated: 2026-08-09
---

# Story 2.3: Objection handling guidance

## User Story
**As a** sales rep  
**I want to** ask "How should I handle a pricing objection from an enterprise customer?"  
**So that** I can get grounded sales advice from company playbooks and best practices

## Business Value
This story delivers the first user-facing RAG capability, demonstrating retrieval-augmented generation where the agent grounds responses in actual company knowledge rather than hallucinating advice. It proves the RAG architecture pattern: natural language question → semantic search → knowledge retrieval → context-grounded response. This is a critical differentiator from pure LLM responses and validates the value of enterprise knowledge bases integrated with conversational AI.

## Acceptance Criteria
```gherkin
Given the FastAPI application is running
And the FAISS knowledge base contains sales playbook documents
And the playbook includes pricing and objection handling guidance
When the user asks "How should I handle a pricing objection from an enterprise customer?"
Then the agent retrieves relevant RAG documents from FAISS
And the response includes at least one concrete recommendation
And the answer references pricing or objection-handling guidance from the knowledge base
And the response cites or paraphrases retrieved content (not generic LLM advice)
And the retrieval process uses semantic search over embeddings
```

## Technical Requirements

### Stack & Dependencies
- **Python**: 3.11+ (consistent with Epic 1)
- **LangChain**: Extend existing `langchain-anthropic` setup from Story 1.1
- **Claude API**: Continue using Claude 3.5 Sonnet or Haiku
- **FAISS**: `faiss-cpu` for local vector store (or `faiss-gpu` if available)
- **Embeddings**: Use OpenAI embeddings (`text-embedding-3-small`) or Anthropic embeddings (choose lower-cost option)
- **LangChain FAISS**: `langchain-community` for FAISS vector store integration
- **Document Loaders**: `langchain` text loaders for markdown/txt playbook files
- **FastAPI**: Existing FastAPI app from Epic 1 (no new dependencies)
- **Environment**: Add embedding API key to `.env` (OPENAI_API_KEY or ANTHROPIC_API_KEY)

### Architecture Compliance

#### Component Structure
This story implements the **RAG / FAISS Knowledge Store** component and integrates it with the existing **LangChain ReACT Agent** from Epic 1.

**Critical Architecture Points:**
1. **Local FAISS Store**: Use local FAISS index stored on disk - NO remote vector databases
2. **Semantic Retrieval**: Agent retrieves top-N chunks using embedding similarity before generating response
3. **Grounded Responses**: Agent MUST use retrieved content as context - not pure LLM generation
4. **Retrieval Tool**: RAG retrieval is exposed as a tool to the ReACT agent (like MCP tools from Epic 1)
5. **Single FastAPI Process**: All RAG logic runs in the same FastAPI app - no separate RAG service

#### Data Flow (from Architecture - RAG Question Flow)
```
User Query: "How should I handle a pricing objection from an enterprise customer?"
  → FastAPI /agent/query endpoint (EXISTING from Epic 1)
  → LangChain ReACT Agent (EXISTING)
  → Agent reasons: "This requires company knowledge"
  → Agent selects RAG retrieval tool
  → RAG retriever queries FAISS with embedded question
  → FAISS returns top-N relevant document chunks
  → Agent receives chunks as context
  → Agent synthesizes answer grounded in retrieved content
  → Response includes recommendations from playbooks
  → Return to user with cited sources
```

### File Structure Requirements

**Expected NEW Files:**
```
salesflow_agent/
  rag/
    __init__.py
    store.py                 # FAISS vector store initialization and query interface
    retriever.py             # Retrieval tool wrapper for agent integration
    embeddings.py            # Embedding client setup (OpenAI or Anthropic)
    indexer.py               # Document loading and index building utility
data/
  knowledge/
    sales-playbook.md        # Sales methodology and best practices
    pricing-guide.md         # Pricing strategies and enterprise discounting
    objection-handling.md    # Common objections and recommended responses
    product-positioning.md   # Product value propositions
    competitive-intel.md     # Competitor comparison and differentiation
  faiss_index/
    index.faiss              # FAISS vector index file
    index.pkl                # Pickled document metadata (chunks, sources)
scripts/
  build_rag_index.py         # Script to rebuild FAISS index from knowledge docs
```

**Files to UPDATE (from Epic 1):**
```
salesflow_agent/
  main.py                    # Initialize RAG store on startup alongside MCP client
  agent/
    react_agent.py           # Register RAG retrieval tool with agent
    tools.py                 # Add RAG retrieval tool definition
requirements.txt             # Add faiss-cpu, openai (or anthropic for embeddings)
.env.example                 # Add OPENAI_API_KEY or ANTHROPIC_API_KEY
README.md                    # Add RAG index rebuild instructions
```

**Files UNCHANGED:**
```
salesflow_agent/
  mcp/                       # MCP integration from Epic 1 unchanged
data/
  crm.db                     # CRM data from Epic 1 unchanged
```

### Critical Implementation Details

#### 1. FAISS Vector Store (`salesflow_agent/rag/store.py`)
```python
# Must:
# - Initialize FAISS index from disk on app startup
# - Support local persistence (save/load index.faiss and index.pkl)
# - Provide query interface: query(text: str, k: int) -> List[Document]
# - Return document chunks with metadata (source file, chunk index)
# - Handle index not found gracefully (log error, suggest running build script)
```

**Implementation Pattern:**
```python
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings  # or langchain_anthropic
import os

class RAGStore:
    def __init__(self, index_path: str, embeddings_client):
        self.index_path = index_path
        self.embeddings = embeddings_client
        self.vectorstore = None
        
    def load(self):
        """Load existing FAISS index from disk"""
        if os.path.exists(self.index_path):
            self.vectorstore = FAISS.load_local(
                self.index_path, 
                self.embeddings,
                allow_dangerous_deserialization=True
            )
        else:
            raise FileNotFoundError(f"Index not found at {self.index_path}. Run build_rag_index.py first.")
    
    def query(self, query_text: str, k: int = 3) -> List[Document]:
        """Retrieve top-k most relevant chunks"""
        return self.vectorstore.similarity_search(query_text, k=k)
```

#### 2. RAG Retrieval Tool (`salesflow_agent/rag/retriever.py`)
```python
# Must:
# - Wrap RAG store as a LangChain tool
# - Accept query string and optional k parameter
# - Return formatted chunk text with source citations
# - Be registered with the ReACT agent alongside MCP tools
```

**Implementation Pattern:**
```python
from langchain.tools import Tool

def create_rag_retrieval_tool(rag_store: RAGStore) -> Tool:
    """Create a LangChain tool for RAG knowledge retrieval"""
    
    def retrieve_knowledge(query: str) -> str:
        """Retrieve relevant sales knowledge from the knowledge base"""
        docs = rag_store.query(query, k=3)
        
        if not docs:
            return "No relevant knowledge found."
        
        # Format retrieved chunks with source citations
        chunks = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get('source', 'unknown')
            content = doc.page_content
            chunks.append(f"[Source {i}: {source}]\n{content}")
        
        return "\n\n".join(chunks)
    
    return Tool(
        name="retrieve_sales_knowledge",
        description="Retrieve relevant sales playbook content, pricing guidance, objection handling strategies, and best practices. Use this tool when answering questions about sales methodology, pricing, objections, or company-specific advice.",
        func=retrieve_knowledge
    )
```

#### 3. Index Builder Script (`scripts/build_rag_index.py`)
```python
# Must:
# - Load all documents from data/knowledge/
# - Split documents into chunks (500-1000 token chunks with overlap)
# - Embed each chunk using embedding client
# - Build FAISS index and save to data/faiss_index/
# - Log progress and summary statistics
# - Be runnable standalone: python scripts/build_rag_index.py
```

**Implementation Pattern:**
```python
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import os

def build_index():
    # Load all markdown/text files from knowledge directory
    loader = DirectoryLoader(
        "data/knowledge/",
        glob="**/*.md",
        loader_cls=TextLoader
    )
    documents = loader.load()
    print(f"Loaded {len(documents)} documents")
    
    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks")
    
    # Create embeddings and build index
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    
    # Save to disk
    os.makedirs("data/faiss_index", exist_ok=True)
    vectorstore.save_local("data/faiss_index")
    print("Index saved to data/faiss_index/")

if __name__ == "__main__":
    build_index()
```

#### 4. Agent Integration (`salesflow_agent/agent/react_agent.py`)
**REQUIRED CHANGE**: Add RAG retrieval tool to agent's tool list

```python
# Before (from Story 1.1):
agent = create_react_agent(
    llm=claude_llm,
    tools=[mcp_tool_1, mcp_tool_2, ...]
)

# After (for this story):
from salesflow_agent.rag.retriever import create_rag_retrieval_tool

rag_tool = create_rag_retrieval_tool(rag_store)

agent = create_react_agent(
    llm=claude_llm,
    tools=[mcp_tool_1, mcp_tool_2, rag_tool]  # RAG tool added
)
```

#### 5. Knowledge Base Content (`data/knowledge/`)
**REQUIRED**: Create at least 5 sales knowledge documents covering:

**objection-handling.md** (CRITICAL for acceptance criteria):
```markdown
# Objection Handling Guide

## Pricing Objections

### Enterprise Customers - Pricing Too High

**Common Objection**: "Your pricing is 30% higher than competitors."

**Recommended Response Strategy**:
1. **Acknowledge and Validate**: "I understand budget is a key consideration for enterprise deployments."
2. **Reframe Value**: Focus on TCO, not unit price. Highlight reduced integration costs, lower training overhead, and faster time to value.
3. **Quantify ROI**: "Our enterprise customers typically see 40% faster deployment and 25% lower support costs compared to alternatives."
4. **Tiered Flexibility**: Offer volume discounts, multi-year commitments, or phased rollouts to address budget constraints.
5. **Reference Proof Points**: "Companies like [Customer X] chose us despite higher upfront costs because the 3-year TCO was 20% lower."

**When to Discount**: Enterprise deals >$100K can flex up to 15% on approval. Emphasize value first, discount as last resort.

### Mid-Market Pricing Objections
[Additional content...]

## Technical Objections
[Additional content...]
```

**pricing-guide.md**:
```markdown
# Pricing Guide

## Enterprise Tier ($100K+ ARR)

**Standard Pricing**:
- Per-user: $150/user/month (annual commit)
- Platform fee: $25K/year
- Implementation: $15K-$50K one-time

**Discount Authority**:
- Sales rep: up to 10% discretion
- Manager approval: 10-15%
- VP approval: 15-20% (rare, requires strong strategic justification)

**Enterprise Value Props**:
- Dedicated support (4-hour SLA)
- Custom integrations included
- Quarterly business reviews
- Advanced security and compliance (SOC2, HIPAA)

[Additional content...]
```

**sales-playbook.md**, **product-positioning.md**, **competitive-intel.md**: Fill with relevant demo content.

### Testing Requirements

**Acceptance Test Scenarios:**
1. **Primary Test**: User asks "How should I handle a pricing objection from an enterprise customer?" and receives:
   - At least one concrete recommendation from objection-handling.md
   - Reference to pricing strategies from pricing-guide.md
   - Response cites or paraphrases retrieved content (not generic advice)

2. **Variation Query**: User asks "What should I say when a customer says we're too expensive?" and agent handles similar intent

3. **Source Citation**: Response should indicate knowledge came from playbooks (either explicit citation or paraphrasing company guidance)

4. **Retrieval Validation**: Check agent execution trace shows RAG retrieval tool invocation before response generation

5. **No Retrieval Fallback**: If user asks non-knowledge question (e.g., "What are my top deals?"), agent uses MCP tools instead (doesn't force RAG usage)

**Testing Approach:**
- Manual testing via `curl` or API client
- Validate response includes specific guidance from knowledge docs (not hallucinated generic advice)
- Check agent logs show semantic search and chunk retrieval
- Verify FAISS index loaded successfully on app startup
- Test index rebuild script can recreate index from knowledge docs

**Test Data Requirements:**
- Minimum 5 knowledge documents (total ~5000 words)
- objection-handling.md must contain "pricing objection" section with enterprise guidance
- pricing-guide.md must contain enterprise pricing strategies
- Documents should use realistic sales language and scenarios

### Success Criteria Mapping
This story directly implements:
- **FR-3**: Combined answer with RAG context (agent retrieves and cites knowledge)
- **FR-5**: Retrieval during agent response generation
- **SM-2**: Demo returns a grounded answer using RAG content for objection handling

### Dependencies
- **Upstream**: 
  - **Story 2.5** (Build the sales RAG index): This story builds the indexing infrastructure. However, this story (2.3) can be implemented first if we include the index builder as part of the implementation.
  - **Story 1.1** (Conversational pipeline query): Reuses FastAPI app and ReACT agent setup
  
- **Downstream**: 
  - **Story 4.7** (Enrich lead via RAG): Will reuse the RAG store and retrieval interface

**Development Order**: This story can be implemented in parallel with or before Story 2.5 since both involve building the RAG infrastructure. Story 2.3 is the user-facing implementation that includes the indexer.

### Known Constraints
- **Embedding Cost**: OpenAI embeddings cost ~$0.0001 per 1K tokens. With ~5K word corpus, expect <$0.01 to build index. Keep minimal for demo.
- **FAISS Local Only**: No cloud vector stores (Pinecone, Weaviate, etc.). Must use local FAISS for demo simplicity.
- **Chunk Strategy**: Use 800 token chunks with 200 token overlap to balance context and retrieval accuracy.
- **Top-K Retrieval**: Retrieve top 3 chunks by default. More chunks = better context but higher token costs.
- **Index Rebuild**: Index must be rebuilt if knowledge docs change. Include clear instructions in README.

## Implementation Notes for Developer

### Critical Success Factors
1. **Grounded Responses Are Non-Negotiable**: Agent MUST use retrieved content, not generic LLM knowledge. The response should feel like it came from company playbooks.
2. **Semantic Search Quality**: Embedding model and chunking strategy are critical. Test retrieval quality before integrating with agent.
3. **Tool Integration Pattern**: RAG retrieval is a tool like MCP tools - agent should reason about when to use it.
4. **Index Availability**: App must fail gracefully if index missing. Log clear error directing user to run build script.

### Recommended Development Sequence
1. **Phase 1: Knowledge Content Creation**
   - Write 5 sales knowledge documents in `data/knowledge/`
   - Focus on objection-handling.md with enterprise pricing objection section
   - Ensure realistic, specific content (not generic advice)

2. **Phase 2: Index Builder**
   - Implement `scripts/build_rag_index.py`
   - Test document loading, chunking, and embedding
   - Verify index saved to `data/faiss_index/`
   - Validate index size and chunk count

3. **Phase 3: RAG Store**
   - Implement `salesflow_agent/rag/store.py`
   - Test index loading from disk
   - Test query interface with sample questions
   - Verify chunks returned with source metadata

4. **Phase 4: Retrieval Tool**
   - Implement `salesflow_agent/rag/retriever.py`
   - Wrap RAG store as LangChain tool
   - Test tool independently (call retrieve function directly)
   - Validate formatted output includes sources

5. **Phase 5: Agent Integration**
   - Update `salesflow_agent/main.py` to initialize RAG store on startup
   - Update `salesflow_agent/agent/react_agent.py` to register RAG tool
   - Test end-to-end: user query → agent → RAG retrieval → grounded response

6. **Phase 6: Validation & Polish**
   - Test acceptance criteria scenarios
   - Verify response quality and source citations
   - Check agent reasoning trace shows tool selection
   - Update README with RAG index rebuild instructions
   - Update .env.example with embedding API key

### Potential Pitfalls to Avoid
- **Generic LLM Responses**: If agent doesn't use RAG tool, it will hallucinate generic advice. Ensure tool description clearly indicates when to use it.
- **Poor Chunking**: Chunks too large (>1000 tokens) = high cost. Chunks too small (<500 tokens) = fragmented context. Use 800±200 tokens.
- **Wrong Embedding Model**: Use a cost-effective model. OpenAI `text-embedding-3-small` or Anthropic `claude-3-haiku-embedding` (if available).
- **Index Deserialization Error**: FAISS `load_local` requires `allow_dangerous_deserialization=True` for pickle files. This is safe for local demo.
- **Missing Tool Description**: RAG tool needs clear description so agent knows when to invoke it. Should mention "sales playbook", "objection handling", "pricing guidance", "company knowledge".
- **No Source Attribution**: Chunks should include source file metadata. Format responses to cite sources so user can trace guidance back to playbooks.

### Example Agent Trace (Expected Output)
```
User: "How should I handle a pricing objection from an enterprise customer?"

Agent Reasoning:
  Thought: This question is about sales methodology and objection handling. I should retrieve relevant company knowledge from the sales playbooks.
  Action: retrieve_sales_knowledge
  Action Input: {"query": "pricing objection enterprise customer"}
  
Tool Response:
  [Source 1: data/knowledge/objection-handling.md]
  # Pricing Objections - Enterprise Customers
  
  **Common Objection**: "Your pricing is 30% higher than competitors."
  
  **Recommended Response Strategy**:
  1. Acknowledge and Validate: "I understand budget is a key consideration for enterprise deployments."
  2. Reframe Value: Focus on TCO, not unit price. Highlight reduced integration costs, lower training overhead, and faster time to value.
  3. Quantify ROI: "Our enterprise customers typically see 40% faster deployment and 25% lower support costs compared to alternatives."
  ...
  
  [Source 2: data/knowledge/pricing-guide.md]
  # Enterprise Tier ($100K+ ARR)
  
  **Discount Authority**:
  - Sales rep: up to 10% discretion
  - Manager approval: 10-15%
  - VP approval: 15-20% (rare, requires strong strategic justification)
  ...
  
Final Answer:
  "When handling pricing objections from enterprise customers, I recommend a structured approach based on our sales playbook:

  1. **Acknowledge and Validate**: Start by saying "I understand budget is a key consideration for enterprise deployments." This shows empathy and keeps the conversation open.

  2. **Reframe to Total Cost of Ownership**: Don't defend unit price—shift to TCO. Our enterprise customers typically see 40% faster deployment and 25% lower support costs compared to alternatives, which often offsets the higher upfront cost.

  3. **Quantify ROI**: Use specific proof points. For example, companies like [Customer X] chose us despite higher initial pricing because their 3-year TCO was 20% lower due to reduced integration and support overhead.

  4. **Offer Tiered Flexibility**: If budget remains a concern, explore volume discounts, multi-year commitments, or phased rollouts. You have discretion up to 10% discount, with manager approval for 10-15%.

  The key is to make this about long-term value and strategic fit, not just price comparison. Let me know if you need help positioning specific value points for your customer's use case."
```

### Environment Setup
```bash
# Required environment variables (.env):
ANTHROPIC_API_KEY=sk-ant-...              # Existing from Epic 1
OPENAI_API_KEY=sk-...                     # NEW - for embeddings
MCP_SERVER_URL=http://localhost:8001      # Existing from Epic 1

# Index rebuild:
python scripts/build_rag_index.py

# App startup (after index built):
python -m salesflow_agent
```

### Validation Checklist
Before marking this story complete, verify:
- [ ] Index built successfully with 5+ knowledge documents
- [ ] RAG store loads index from disk on app startup
- [ ] RAG retrieval tool registered with agent
- [ ] User query about pricing objections retrieves relevant chunks
- [ ] Response includes concrete recommendations from objection-handling.md
- [ ] Response cites or paraphrases company playbook content (not generic advice)
- [ ] Agent logs show RAG tool invocation and chunk retrieval
- [ ] README includes RAG index rebuild instructions
- [ ] .env.example includes embedding API key placeholder

## Dev Agent Record

### Agent Model Used
GitHub Copilot (Claude Sonnet 4.5)

### Debug Log References
TBD - will be populated during implementation

### Completion Notes List
TBD - will be populated during implementation

### File List
TBD - will be populated during implementation
