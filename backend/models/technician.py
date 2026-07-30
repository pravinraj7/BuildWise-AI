"""
BuildWise AI — Technician Models
"""
import enum
import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, Enum, ForeignKey, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class TechnicianStatus(str, enum.Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    ON_LEAVE = "on_leave"
    OFFLINE = "offline"


class SkillCategory(str, enum.Enum):
    ELECTRICAL = "electrical"
    PLUMBING = "plumbing"
    HVAC = "hvac"
    ELEVATOR = "elevator"
    FIRE_SAFETY = "fire_safety"
    GENERAL = "general"


class Technician(Base):
    __tablename__ = "technicians"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id: Mapped[str | None] = mapped_column(String(50), unique=True)
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), unique=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str | None] = mapped_column(String(255))
    avatar_url: Mapped[str | None] = mapped_column(String(512))

    skills: Mapped[list | None] = mapped_column(JSON)
    certifications: Mapped[list | None] = mapped_column(JSON)
    experience_years: Mapped[float] = mapped_column(Float, default=1.0)
    hourly_rate: Mapped[float] = mapped_column(Float, default=50.0)
    rating: Mapped[float] = mapped_column(Float, default=5.0)
    specialization: Mapped[str | None] = mapped_column(String(255))

    status: Mapped[TechnicianStatus] = mapped_column(Enum(TechnicianStatus), default=TechnicianStatus.AVAILABLE)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    current_workload: Mapped[int] = mapped_column(Integer, default=0)
    max_concurrent_jobs: Mapped[int] = mapped_column(Integer, default=3)
    performance_score: Mapped[float] = mapped_column(Float, default=90.0)
    assigned_building_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("buildings.id"))

    # Job stats
    total_jobs: Mapped[int] = mapped_column(Integer, default=0)
    completed_jobs: Mapped[int] = mapped_column(Integer, default=0)
    avg_resolution_time_hours: Mapped[float] = mapped_column(Float, default=0.0)
    current_location: Mapped[str | None] = mapped_column(String(255))

    # Shift info
    shift_start: Mapped[str | None] = mapped_column(String(10), default="09:00")
    shift_end: Mapped[str | None] = mapped_column(String(10), default="18:00")
    work_days: Mapped[list | None] = mapped_column(JSON, default=lambda: ["Mon", "Tue", "Wed", "Thu", "Fri"])

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    user: Mapped["User | None"] = relationship("User", back_populates="technician_profile")
    assigned_building: Mapped["Building | None"] = relationship("Building", back_populates="technicians")
    complaints: Mapped[list["Complaint"]] = relationship("Complaint", back_populates="technician")
