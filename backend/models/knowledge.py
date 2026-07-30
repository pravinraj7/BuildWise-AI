"""
BuildWise AI — Knowledge Base & Document Models
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), default="general")
    description: Mapped[str | None] = mapped_column(Text)
    file_path: Mapped[str | None] = mapped_column(String(500))
    file_name: Mapped[str | None] = mapped_column(String(255))
    file_url: Mapped[str | None] = mapped_column(String(500))
    file_type: Mapped[str | None] = mapped_column(String(50))
    file_size_bytes: Mapped[int | None] = mapped_column(Integer)
    document_type: Mapped[str | None] = mapped_column(String(50), default="manual")
    equipment_type: Mapped[str | None] = mapped_column(String(100))

    building_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("buildings.id"))
    uploaded_by_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    is_indexed: Mapped[bool] = mapped_column(Boolean, default=False)
    indexed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    chroma_collection_id: Mapped[str | None] = mapped_column(String(100))
    tags: Mapped[list | None] = mapped_column(JSON, default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("knowledge_documents.id"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
