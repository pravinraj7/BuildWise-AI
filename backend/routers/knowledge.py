"""
BuildWise AI — Knowledge Base Router (RAG + Document Upload)
"""
import os
import aiofiles
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, BackgroundTasks, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, List

from database import get_db
from models.knowledge import KnowledgeDocument
from models.user import User
from services.jwt_service import get_current_user
from config import settings

router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    limit: int = 5
    document_type: Optional[str] = None


class ChatRequest(BaseModel):
    question: str
    context: Optional[str] = None


@router.post("/upload", status_code=201)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(""),
    description: str = Form(""),
    document_type: str = Form("manual"),
    building_id: Optional[str] = Form(None),
    equipment_type: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    allowed_types = {"application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, and TXT files are allowed")

    # Save file
    docs_dir = os.path.join(settings.UPLOAD_DIR, "documents")
    os.makedirs(docs_dir, exist_ok=True)
    file_path = os.path.join(docs_dir, file.filename)

    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    # Create DB record
    doc = KnowledgeDocument(
        title=title or file.filename,
        description=description,
        file_path=file_path,
        file_name=file.filename,
        file_url=f"/uploads/documents/{file.filename}",
        file_type=file.filename.rsplit(".", 1)[-1].lower(),
        file_size_bytes=len(content),
        document_type=document_type,
        building_id=building_id,
        equipment_type=equipment_type,
        uploaded_by_id=current_user.id,
    )
    db.add(doc)
    await db.flush()
    await db.commit()

    # Index in ChromaDB in background
    background_tasks.add_task(_index_document, doc.id, file_path)

    return {
        "id": doc.id, "title": doc.title, "file_name": doc.file_name,
        "file_type": doc.file_type, "document_type": doc.document_type,
        "is_indexed": doc.is_indexed, "created_at": doc.created_at.isoformat(),
    }


@router.get("")
async def list_documents(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(KnowledgeDocument).order_by(KnowledgeDocument.created_at.desc()))
    docs = result.scalars().all()
    return [
        {
            "id": d.id, "title": d.title, "description": d.description,
            "file_name": d.file_name, "file_type": d.file_type,
            "document_type": d.document_type, "tags": d.tags,
            "is_indexed": d.is_indexed, "chunk_count": d.chunk_count,
            "created_at": d.created_at.isoformat(),
        }
        for d in docs
    ]


@router.post("/search")
async def search_documents(payload: SearchRequest, current_user: User = Depends(get_current_user)):
    from services.rag_service import search_knowledge_base
    results = await search_knowledge_base(payload.query, payload.limit)
    return {"query": payload.query, "results": results}


@router.post("/chat")
async def chat_with_knowledge_base(payload: ChatRequest, current_user: User = Depends(get_current_user)):
    from services.rag_service import query_knowledge_base
    result = await query_knowledge_base(payload.question, payload.context or "")
    return result


@router.delete("/{doc_id}", status_code=204)
async def delete_document(doc_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(KnowledgeDocument).where(KnowledgeDocument.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    await db.delete(doc)
    await db.commit()



async def _index_document(doc_id: str, file_path: str):
    print(">>> Background task started")
    print(f">>> Doc ID: {doc_id}")
    print(f">>> File Path: {file_path}")

    try:
        from services.rag_service import index_document

        success = await index_document(doc_id, file_path)

        print(f">>> Indexing completed: {success}")

    except Exception:
        import traceback
        traceback.print_exc()

        import structlog
        structlog.get_logger().error(
            "Document indexing failed",
            doc_id=doc_id,
            error=traceback.format_exc()
        )