"""
BuildWise AI — RAG Service (ChromaDB + Sentence Transformers)
"""
import os
import uuid
import asyncio
import structlog
from typing import List, Optional
from config import settings

logger = structlog.get_logger()

_chroma_client = None
_collection = None
_embedding_model = None  # Cached sentence-transformers model


def _get_embedding_model():
    """Lazy-load and cache the sentence-transformers model."""
    global _embedding_model
    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("SentenceTransformer model loaded and cached")
        except Exception as e:
            logger.warning(f"SentenceTransformer load failed: {e}")
    return _embedding_model


def get_chroma_client():
    global _chroma_client, _collection

    print(">>> get_chroma_client() called")

    if _chroma_client is None:
        import chromadb
        import os

        try:
            print(">>> Creating chroma_db folder")
            os.makedirs("./chroma_db", exist_ok=True)

            print(">>> Initializing PersistentClient")
            _chroma_client = chromadb.PersistentClient(
                path="./chroma_db"
            )

            print(">>> Creating collection")
            _collection = _chroma_client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION,
                metadata={"hnsw:space": "cosine"}
            )

            print(">>> ChromaDB ready")
            logger.info("Persistent ChromaDB initialized successfully")

        except Exception as e:
            print(f">>> ERROR: {e}")
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise

    return _chroma_client, _collection

async def index_document(doc_id: str, file_path: str) -> bool:
    """Parse, chunk, and embed a document into ChromaDB."""

    print(">>> index_document() started")
    print(f">>> File: {file_path}")

    try:
        # Extract text
        text = _extract_text(file_path)

        if not text:
            logger.error(f"Unable to extract text from {file_path}")

            from database import AsyncSessionLocal
            from models.knowledge import KnowledgeDocument
            from sqlalchemy import select

            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(KnowledgeDocument).where(
                        KnowledgeDocument.id == doc_id
                    )
                )

                doc = result.scalar_one_or_none()

                if doc:
                    doc.is_indexed = False
                    doc.chunk_count = 0
                    await db.commit()

            return False

        print(">>> Text extracted")

        # Split into chunks
        chunks = _chunk_text(
            text,
            chunk_size=500,
            overlap=50
        )

        print(f">>> Created {len(chunks)} chunks")

        # Connect to ChromaDB
        _, collection = get_chroma_client()

        print(">>> Connected to ChromaDB")

        # Generate embeddings
        embeddings = _embed_texts(chunks)

        print(">>> Embeddings generated")

        # Store in ChromaDB
        collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=[
                f"{doc_id}_{i}"
                for i in range(len(chunks))
            ],
            metadatas=[
                {
                    "doc_id": doc_id,
                    "chunk_index": i,
                    "source": os.path.basename(file_path),
                }
                for i in range(len(chunks))
            ],
        )

        print(">>> Stored in ChromaDB")

        # Update database
        from database import AsyncSessionLocal
        from models.knowledge import KnowledgeDocument
        from sqlalchemy import select
        from datetime import datetime

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(KnowledgeDocument).where(
                    KnowledgeDocument.id == doc_id
                )
            )

            doc = result.scalar_one_or_none()

            if doc:
                doc.is_indexed = True
                doc.chunk_count = len(chunks)
                doc.indexed_at = datetime.utcnow()
                doc.chroma_collection_id = settings.CHROMA_COLLECTION

                await db.commit()

        print(">>> Database updated")

        logger.info(
            "Document indexed",
            doc_id=doc_id,
            chunks=len(chunks)
        )

        print(">>> index_document() completed")

        return True

    except Exception as e:
        import traceback

        traceback.print_exc()

        logger.error(
            "Document indexing failed",
            doc_id=doc_id,
            error=str(e)
        )

        return False
        
async def search_knowledge_base(query: str, limit: int = 5) -> List[dict]:
    """Semantic search in ChromaDB."""
    try:
        _, collection = get_chroma_client()
        query_embedding = _embed_texts([query])[0]
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(limit, max(1, collection.count())),
            include=["documents", "metadatas", "distances"],
        )

        output = []
        if results and results["documents"]:
            for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
                output.append({
                    "text": doc,
                    "source": meta.get("source", ""),
                    "doc_id": meta.get("doc_id", ""),
                    "similarity": round(1 - dist, 3),
                })
        return output
    except Exception as e:
        logger.warning(f"Knowledge base search failed: {e}")
        return []


async def query_knowledge_base(question: str, context: str = "") -> dict:
    """RAG: search + LLM answer."""
    results = await search_knowledge_base(question, limit=3)
    context_text = "\n\n".join([r["text"] for r in results])

    if not context_text:
        context_text = "No relevant documents found in the knowledge base."

    prompt = f"""You are a building maintenance expert assistant.
Use the following context from the knowledge base to answer the question.

Context:
{context_text}

Question: {question}

Provide a clear, helpful answer based on the context. If the context doesn't contain enough information, say so."""

    try:
        from config import settings
        if settings.OPENAI_API_KEY:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import HumanMessage
            llm = ChatOpenAI(model=settings.LLM_MODEL, api_key=settings.OPENAI_API_KEY, temperature=0.1)
            response = llm.invoke([HumanMessage(content=prompt)])
            answer = response.content
        else:
            answer = f"Based on retrieved documents: {context_text[:500]}..."
    except Exception as e:
        answer = f"Based on the knowledge base: {context_text[:300]}..."

    return {
        "question": question,
        "answer": answer,
        "sources": [r["source"] for r in results],
        "retrieved_docs": len(results),
    }


def _extract_text(file_path: str) -> str:
    """Extract text from PDF, DOCX, or TXT files."""
    ext = file_path.rsplit(".", 1)[-1].lower()
    try:
        if ext == "pdf":
            import fitz
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        elif ext == "docx":
            from docx import Document
            doc = Document(file_path)
            return "\n".join(para.text for para in doc.paragraphs)
        elif ext == "txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
    except Exception as e:
        logger.error(f"Text extraction failed: {e}")
    return ""


def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks or [text[:1000]]


def _embed_texts(texts: List[str]) -> List[List[float]]:
    """Generate embeddings using cached sentence-transformers model."""
    model = _get_embedding_model()
    if model is not None:
        try:
            return model.encode(texts).tolist()
        except Exception as e:
            logger.warning(f"Embedding failed: {e}, using random embeddings")
    import random
    return [[random.random() for _ in range(384)] for _ in texts]
