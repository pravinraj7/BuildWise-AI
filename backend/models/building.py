"""
BuildWise AI — Building Hierarchy Models
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Building(Base):
    __tablename__ = "buildings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    building_type: Mapped[str] = mapped_column(String(100), default="office")
    address: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True, default="")
    state: Mapped[str | None] = mapped_column(String(100), nullable=True, default="")
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True, default="")
    country: Mapped[str] = mapped_column(String(100), default="India")

    total_floors: Mapped[int] = mapped_column(Integer, default=1)
    total_area_sqft: Mapped[float | None] = mapped_column(Float)
    built_year: Mapped[int | None] = mapped_column(Integer)
    health_score: Mapped[int] = mapped_column(Integer, default=100)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    manager_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    floors: Mapped[list["Floor"]] = relationship("Floor", back_populates="building", cascade="all, delete-orphan")
    departments: Mapped[list["Department"]] = relationship("Department", back_populates="building", cascade="all, delete-orphan")
    complaints: Mapped[list["Complaint"]] = relationship("Complaint", back_populates="building")
    technicians: Mapped[list["Technician"]] = relationship("Technician", back_populates="assigned_building")


class Floor(Base):
    __tablename__ = "floors"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    building_id: Mapped[str] = mapped_column(String(36), ForeignKey("buildings.id"), nullable=False)
    floor_number: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(100))
    area_sqft: Mapped[float | None] = mapped_column(Float)

    building: Mapped["Building"] = relationship("Building", back_populates="floors")
    rooms: Mapped[list["Room"]] = relationship("Room", back_populates="floor", cascade="all, delete-orphan")


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    building_id: Mapped[str] = mapped_column(String(36), ForeignKey("buildings.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str | None] = mapped_column(String(50))
    floor_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("floors.id"))

    building: Mapped["Building"] = relationship("Building", back_populates="departments")
    rooms: Mapped[list["Room"]] = relationship("Room", back_populates="department")


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    floor_id: Mapped[str] = mapped_column(String(36), ForeignKey("floors.id"), nullable=False)
    room_number: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str | None] = mapped_column(String(100))
    department_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("departments.id"))
    area_sqft: Mapped[float | None] = mapped_column(Float)

    floor: Mapped["Floor"] = relationship("Floor", back_populates="rooms")
    department: Mapped["Department | None"] = relationship("Department", back_populates="rooms")
