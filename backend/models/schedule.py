"""
BuildWise AI — Schedule Models
"""
import enum
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Enum, ForeignKey, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class ScheduleStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


class Schedule(Base):
    __tablename__ = "schedules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    complaint_id: Mapped[str] = mapped_column(String(36), ForeignKey("complaints.id"), nullable=False)
    technician_id: Mapped[str] = mapped_column(String(36), ForeignKey("technicians.id"), nullable=False)

    scheduled_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    scheduled_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[ScheduleStatus] = mapped_column(Enum(ScheduleStatus), default=ScheduleStatus.SCHEDULED)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class ScheduleSlot(Base):
    __tablename__ = "schedule_slots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    complaint_id: Mapped[str] = mapped_column(String(36), ForeignKey("complaints.id"), nullable=False)
    technician_id: Mapped[str] = mapped_column(String(36), ForeignKey("technicians.id"), nullable=False)

    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
