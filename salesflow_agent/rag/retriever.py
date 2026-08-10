"""RAG retriever - provides semantic search over the FAISS knowledge base."""

import logging
from pathlib import Path

from langchain_core.vectorstores import VectorStoreRetriever

from salesflow_agent.rag.index_builder import load_index

logger = logging.getLogger(__name__)


def get_retriever(embeddings, top_k: int = 3) -> VectorStoreRetriever:
    """Get a LangChain retriever backed by the FAISS index."""
    vectorstore = load_index(embeddings)
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": top_k},
    )
    logger.info(f"RAG retriever ready (top_k={top_k})")
    return retriever
