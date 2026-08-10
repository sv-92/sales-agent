"""RAG index builder - embeds sales knowledge documents into FAISS."""

import logging
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
KNOWLEDGE_DIR = DATA_DIR / "knowledge"
INDEX_DIR = DATA_DIR / "faiss_index"


def build_index(embeddings) -> FAISS:
    """Build FAISS index from knowledge documents."""
    documents = _load_documents()
    if not documents:
        raise ValueError(f"No documents found in {KNOWLEDGE_DIR}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n## ", "\n### ", "\n\n", "\n", " "],
    )
    chunks = splitter.split_documents(documents)
    logger.info(f"Split {len(documents)} documents into {len(chunks)} chunks")

    vectorstore = FAISS.from_documents(chunks, embeddings)

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(INDEX_DIR))
    logger.info(f"FAISS index saved to {INDEX_DIR}")

    return vectorstore


def load_index(embeddings) -> FAISS:
    """Load existing FAISS index or build if missing."""
    if (INDEX_DIR / "index.faiss").exists():
        logger.info("Loading existing FAISS index")
        return FAISS.load_local(
            str(INDEX_DIR), embeddings, allow_dangerous_deserialization=True
        )
    logger.info("No existing index found, building from documents")
    return build_index(embeddings)


def _load_documents() -> list[Document]:
    """Load all markdown documents from the knowledge directory."""
    documents = []
    if not KNOWLEDGE_DIR.exists():
        logger.warning(f"Knowledge directory not found: {KNOWLEDGE_DIR}")
        return documents

    for md_file in sorted(KNOWLEDGE_DIR.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        doc = Document(
            page_content=content,
            metadata={"source": md_file.name},
        )
        documents.append(doc)
        logger.info(f"Loaded knowledge document: {md_file.name}")

    return documents
