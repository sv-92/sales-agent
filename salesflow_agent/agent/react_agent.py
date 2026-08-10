"""LangChain ReACT Agent with dynamic MCP tool discovery and RAG retrieval."""

import logging
from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import StructuredTool
from langgraph.prebuilt import create_react_agent

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are SalesFlow, an AI sales assistant. You help sales representatives with:
- Pipeline and deal information from the CRM
- Sales forecasts and projections
- Objection handling and sales methodology guidance
- Account and contact lookup
- Lead qualification workflows

When answering questions:
1. Use your available tools to look up real data from the CRM
2. Search the knowledge base for sales methodology and best practices
3. Provide specific, actionable answers grounded in data or company knowledge
4. If you don't have relevant information, say so clearly

Always be concise and professional. Format financial data with dollar signs and commas."""


class SalesFlowAgent:
    """ReACT agent that uses MCP tools and RAG retrieval for sales assistance."""

    def __init__(self, tools: list[StructuredTool], model_name: str = "claude-3-5-sonnet-20240620"):
        self.llm = ChatAnthropic(model=model_name, temperature=0)
        self.tools = tools
        self.agent = create_react_agent(
            self.llm,
            tools=self.tools,
            prompt=SystemMessage(content=SYSTEM_PROMPT),
        )
        logger.info(f"Agent initialized with {len(tools)} tools: {[t.name for t in tools]}")

    async def query(self, message: str) -> dict[str, Any]:
        """Process a user query through the ReACT agent."""
        result = await self.agent.ainvoke(
            {"messages": [HumanMessage(content=message)]}
        )

        # Extract the final response and tools used
        messages = result["messages"]
        final_message = messages[-1]
        answer = final_message.content if hasattr(final_message, "content") else str(final_message)

        # Track which tools were invoked
        tools_used = []
        for msg in messages:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    tools_used.append(tc["name"])

        return {
            "answer": answer,
            "tools_used": tools_used,
        }
