"""
BuildWise AI — Complaint Models
"""
import enum
import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, Enum, Text, ForeignKey, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class ComplaintStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    AI_PROCESSING = "ai_processing"
    DIAGNOSED = "diagnosed"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REOPENED = "reopened"


class PriorityLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class ComplaintCategory(str, enum.Enum):
    ELECTRICAL = "electrical"
    PLUMBING = "plumbing"
    HVAC = "hvac"
    STRUCTURAL = "structural"
    ELEVATOR = "elevator"
    FIRE_SAFETY = "fire_safety"
    SECURITY = "security"
    CLEANING = "cleaning"
    IT_NETWORK = "it_network"
    GENERAL = "general"


class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    # Requester & Location
    requester_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    building_id: Mapped[str] = mapped_column(String(36), ForeignKey("buildings.id"), nullable=False)
    floor_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("floors.id"))
    room_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("rooms.id"))
    department_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("departments.id"))
    location_description: Mapped[str | None] = mapped_column(Text)

    # Complaint Details
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[ComplaintCategory] = mapped_column(Enum(ComplaintCategory), default=ComplaintCategory.GENERAL)
    status: Mapped[ComplaintStatus] = mapped_column(Enum(ComplaintStatus), default=ComplaintStatus.SUBMITTED)
    priority: Mapped[PriorityLevel] = mapped_column(Enum(PriorityLevel), default=PriorityLevel.MEDIUM)

    # AI Analysis Results
    ai_diagnosis: Mapped[str | None] = mapped_column(Text)
    ai_suggested_repair: Mapped[str | None] = mapped_column(Text)
    ai_suggested_parts: Mapped[list | None] = mapped_column(JSON)
    ai_confidence_score: Mapped[float | None] = mapped_column(Float)
    ai_processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Assignment
    assigned_technician_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("technicians.id"))
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Cost Estimates
    estimated_labor_cost: Mapped[float | None] = mapped_column(Float)
    estimated_material_cost: Mapped[float | None] = mapped_column(Float)
    estimated_total_cost: Mapped[float | None] = mapped_column(Float)
    actual_cost: Mapped[float | None] = mapped_column(Float)
    estimated_duration_hours: Mapped[float | None] = mapped_column(Float)

    # Ratings
    resolution_rating: Mapped[int | None] = mapped_column(Integer)
    resolution_feedback: Mapped[str | None] = mapped_column(Text)

    # Misc
    is_emergency: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_evacuation: Mapped[bool] = mapped_column(Boolean, default=False)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    requester: Mapped["User"] = relationship("User", back_populates="complaints", foreign_keys=[requester_id])
    building: Mapped["Building"] = relationship("Building", back_populates="complaints")
    technician: Mapped["Technician | None"] = relationship("Technician", back_populates="complaints", foreign_keys=[assigned_technician_id])
    attachments: Mapped[list["ComplaintAttachment"]] = relationship("ComplaintAttachment", back_populates="complaint", cascade="all, delete-orphan")
    timeline: Mapped[list["ComplaintTimeline"]] = relationship("ComplaintTimeline", back_populates="complaint", cascade="all, delete-orphan", order_by="ComplaintTimeline.created_at")


class ComplaintAttachment(Base):
    __tablename__ = "complaint_attachments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    complaint_id: Mapped[str] = mapped_column(String(36), ForeignKey("complaints.id"), nullable=False)
    file_type: Mapped[str] = mapped_column(String(20))
    file_name: Mapped[str] = mapped_column(String(255))
    file_url: Mapped[str] = mapped_column(String(500))
    file_size_bytes: Mapped[int | None] = mapped_column(Integer)
    cv_analysis: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    complaint: Mapped["Complaint"] = relationship("Complaint", back_populates="attachments")


class ComplaintTimeline(Base):
    __tablename__ = "complaint_timeline"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    complaint_id: Mapped[str] = mapped_column(String(36), ForeignKey("complaints.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    actor_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    actor_name: Mapped[str | None] = mapped_column(String(255))
    actor_type: Mapped[str] = mapped_column(String(50), default="system")
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    complaint: Mapped["Complaint"] = relationship("Complaint", back_populates="timeline")
