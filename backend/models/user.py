"""
BuildWise AI — User & Authentication Models
"""
import enum
import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    FACILITY_MANAGER = "facility_manager"
    BUILDING_ADMIN = "building_admin"
    TECHNICIAN = "technician"
    TENANT = "tenant"
    RESIDENT = "resident"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, default=lambda: str(uuid.uuid4())[:8])
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.RESIDENT)
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    department: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    building_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("buildings.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    complaints: Mapped[list["Complaint"]] = relationship("Complaint", back_populates="requester", foreign_keys="Complaint.requester_id")
    technician_profile: Mapped["Technician | None"] = relationship("Technician", back_populates="user", uselist=False)
