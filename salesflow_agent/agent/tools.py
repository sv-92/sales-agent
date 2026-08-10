"""RAG retriever tool for the agent."""

from langchain_core.tools import StructuredTool


def create_rag_tool(retriever) -> StructuredTool:
    """Create a LangChain tool that searches the sales knowledge base."""

    async def search_knowledge_base(query: str) -> str:
        """Search the sales knowledge base for relevant guidance, playbooks, and best practices."""
        docs = await retriever.ainvoke(query)
        if not docs:
            return "No relevant knowledge found for this query."
        results = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "unknown")
            results.append(f"[{i}] Source: {source}\n{doc.page_content}")
        return "\n\n---\n\n".join(results)

    return StructuredTool.from_function(
        coroutine=search_knowledge_base,
        name="search_knowledge_base",
        description="Search the sales knowledge base for methodology, objection handling, pricing guidance, negotiation tactics, and best practices. Use this when the user asks for advice or guidance.",
    )
