"""Enrichment worker - enriches leads with RAG knowledge context."""

import logging

logger = logging.getLogger(__name__)


async def enrich_lead(company_name: str, industry: str | None = None, **kwargs) -> dict:
    """Enrich a lead by searching the knowledge base for relevant context."""
    from langchain_openai import OpenAIEmbeddings

    from salesflow_agent.rag.retriever import get_retriever

    query = f"{company_name} {industry or ''} sales approach"
    logger.info(f"Enriching lead: query='{query}'")

    try:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        retriever = get_retriever(embeddings)
        docs = await retriever.ainvoke(query)

        if docs:
            enrichment_text = "\n\n".join(doc.page_content for doc in docs[:3])
            logger.info(f"Enrichment found {len(docs)} relevant chunks")
        else:
            enrichment_text = "No relevant enrichment context available."
            logger.info("No enrichment results found")

    except Exception as e:
        logger.error(f"Enrichment failed: {e}")
        enrichment_text = "Enrichment unavailable due to system error."

    return {"enrichment_text": enrichment_text}
