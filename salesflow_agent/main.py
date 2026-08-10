"""FastAPI application - main entry point for SalesFlow Agent."""

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse

from salesflow_agent.agent.react_agent import SalesFlowAgent
from salesflow_agent.agent.demo_mode import DemoAgent
from salesflow_agent.agent.tools import create_rag_tool
from salesflow_agent.mcp.client import MCPClientWrapper
from salesflow_agent.models.schemas import LeadRequest, LeadResponse, QueryRequest, QueryResponse
from salesflow_agent.rag.retriever import get_retriever
from salesflow_agent.workflows.client import WorkflowClient
from salesflow_agent.workflows.workers.enrichment_worker import enrich_lead
from salesflow_agent.workflows.workers.scoring_worker import score_lead

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

agent: SalesFlowAgent | None = None
workflow_client: WorkflowClient | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize agent with MCP tools and RAG on startup."""
    global agent

    mcp_port = os.environ.get("MCP_SERVER_PORT", "8001")
    mcp_url = f"http://127.0.0.1:{mcp_port}/mcp"

    # Discover MCP tools
    tools = []
    try:
        mcp_client = MCPClientWrapper(mcp_url)
        mcp_tools = await mcp_client.discover_tools()
        tools.extend(mcp_tools)
        logger.info(f"MCP tools discovered: {[t.name for t in mcp_tools]}")
    except Exception as e:
        logger.warning(f"MCP tool discovery failed (server may not be running): {e}")

    # Initialize RAG retriever (disabled for demo - embeddings require PyTorch)
    # To enable: install sentence-transformers on ARM Mac or use OpenAI embeddings
    try:
        # Uncomment when embeddings are available:
        # from langchain_community.embeddings import HuggingFaceEmbeddings
        # embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        # retriever = get_retriever(embeddings)
        # rag_tool = create_rag_tool(retriever)
        # tools.append(rag_tool)
        logger.info("RAG retriever skipped (embeddings not installed)")
    except Exception as e:
        logger.warning(f"RAG initialization failed: {e}")

    # Create agent (use demo mode if enabled or if API key doesn't work)
    demo_mode = os.environ.get("DEMO_MODE", "false").lower() == "true"
    
    if demo_mode:
        agent = DemoAgent(tools=tools)
        logger.info("🎭 Demo mode enabled - using simulated responses")
    else:
        try:
            agent = SalesFlowAgent(tools=tools)
            logger.info("SalesFlow Agent ready")
        except Exception as e:
            logger.warning(f"Failed to initialize LLM agent: {e}")
            logger.info("🎭 Falling back to demo mode")
            agent = DemoAgent(tools=tools)
            demo_mode = True

    # Initialize workflow client (optional — degrades gracefully)
    workflow_client = WorkflowClient()

    yield

    agent = None
    workflow_client = None


app = FastAPI(
    title="SalesFlow Agent",
    description="GenAI Sales Assistant with ReACT, RAG, MCP, and Workflow orchestration",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """Serve the chat UI."""
    static_dir = Path(__file__).parent / "static"
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "SalesFlow Agent API", "docs": "/docs"}


@app.post("/agent/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest) -> QueryResponse:
    """Send a natural language query to the sales agent."""
    if agent is None:
        return QueryResponse(answer="Agent not initialized", tools_used=[], sources=[])

    result = await agent.query(request.message)
    return QueryResponse(
        answer=result["answer"],
        tools_used=result["tools_used"],
        sources=[],
    )


@app.get("/tools")
async def list_tools():
    """List all MCP tools discovered by the agent."""
    if agent is None:
        return {"tools": [], "count": 0, "status": "agent_not_initialized"}
    
    tool_details = [
        {
            "name": tool.name,
            "description": tool.description,
        }
        for tool in agent.tools
    ]
    return {
        "tools": tool_details,
        "count": len(tool_details),
        "status": "ready",
        "mcp_server": f"http://localhost:{os.environ.get('MCP_SERVER_PORT', '8001')}",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "agent_ready": agent is not None}


@app.post("/leads/qualify", response_model=LeadResponse)
async def qualify_lead(request: LeadRequest) -> LeadResponse:
    """Submit a lead for qualification workflow (enrich + score + route)."""
    lead_data = request.model_dump()

    # If Zeebe is available, start the full workflow
    if workflow_client and workflow_client.available:
        instance_key = await workflow_client.start_lead_qualification(lead_data)
        return LeadResponse(
            instance_key=instance_key,
            status="workflow_started",
            message=f"Lead qualification workflow started for {request.company_name}",
        )

    # Fallback: run enrichment + scoring directly (no Zeebe)
    enrichment = await enrich_lead(
        company_name=request.company_name,
        industry=request.industry,
    )
    scoring = await score_lead(
        company_name=request.company_name,
        industry=request.industry,
        enrichment_text=enrichment["enrichment_text"],
    )

    return LeadResponse(
        instance_key=None,
        status=scoring["route_decision"],
        message=(
            f"Lead: {request.company_name} | "
            f"Score: {scoring['lead_score']}/100 | "
            f"Route: {scoring['route_decision']} | "
            f"Reason: {scoring['score_reasoning']}"
        ),
    )
