"""
BuildWise AI — Equipment & Assets Models
"""
import enum
import uuid
from datetime import datetime
from sqlalchemy import String, Float, DateTime, Enum, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class EquipmentStatus(str, enum.Enum):
    OPERATIONAL = "operational"
    NEEDS_MAINTENANCE = "needs_maintenance"
    UNDER_REPAIR = "under_repair"
    DECOMMISSIONED = "decommissioned"
    CRITICAL_FAILURE = "critical_failure"


class EquipmentCategory(str, enum.Enum):
    HVAC = "hvac"
    ELEVATOR = "elevator"
    ELECTRICAL = "electrical"
    PLUMBING = "plumbing"
    FIRE_SAFETY = "fire_safety"
    GENERATOR = "generator"
    PUMP = "pump"
    OTHER = "other"


class Equipment(Base):
    __tablename__ = "equipment"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    building_id: Mapped[str] = mapped_column(String(36), ForeignKey("buildings.id"), nullable=False)
    floor_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("floors.id"))

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    serial_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    category: Mapped[EquipmentCategory] = mapped_column(Enum(EquipmentCategory), nullable=False)
    model_number: Mapped[str | None] = mapped_column(String(100))
    manufacturer: Mapped[str | None] = mapped_column(String(100))

    installation_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_maintenance_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    next_scheduled_maintenance: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    status: Mapped[EquipmentStatus] = mapped_column(Enum(EquipmentStatus), default=EquipmentStatus.OPERATIONAL)
    health_score: Mapped[float] = mapped_column(Float, default=100.0)

    specs: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    maintenance_records: Mapped[list["MaintenanceRecord"]] = relationship("MaintenanceRecord", back_populates="equipment", cascade="all, delete-orphan")
    predictions: Mapped[list["FailurePrediction"]] = relationship("FailurePrediction", back_populates="equipment", cascade="all, delete-orphan")

    @property
    def equipment_type(self) -> str:
        return self.category.value if self.category else "other"

    @property
    def next_maintenance_date(self) -> datetime | None:
        return self.next_scheduled_maintenance

    @next_maintenance_date.setter
    def next_maintenance_date(self, value: datetime | None) -> None:
        self.next_scheduled_maintenance = value

    @property
    def is_critical(self) -> bool:
        return self.health_score < 60 or self.status == EquipmentStatus.CRITICAL_FAILURE

    @property
    def sensor_data(self) -> dict | None:
        return self.specs

    @sensor_data.setter
    def sensor_data(self, value: dict | None) -> None:
        self.specs = value

    @property
    def specifications(self) -> dict | None:
        return self.specs

    @specifications.setter
    def specifications(self, value: dict | None) -> None:
        self.specs = value

    @property
    def failure_probability(self) -> float:
        preds = self.__dict__.get("predictions") or []
        if preds:
            sorted_preds = sorted(preds, key=lambda x: x.created_at or datetime.min, reverse=True)
            return sorted_preds[0].failure_probability
        return 0.05

    @failure_probability.setter
    def failure_probability(self, value: float) -> None:
        pass

    @property
    def remaining_useful_life_days(self) -> int:
        preds = self.__dict__.get("predictions") or []
        if preds:
            sorted_preds = sorted(preds, key=lambda x: x.created_at or datetime.min, reverse=True)
            pred = sorted_preds[0]
            if pred.predicted_failure_date:
                # Ensure timezone naive datetime comparison
                failure_date = pred.predicted_failure_date.replace(tzinfo=None)
                delta = failure_date - datetime.utcnow()
                return max(0, delta.days)
        return 365

    @remaining_useful_life_days.setter
    def remaining_useful_life_days(self, value: int) -> None:
        pass


class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    equipment_id: Mapped[str] = mapped_column(String(36), ForeignKey("equipment.id"), nullable=False)
    complaint_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("complaints.id"))
    technician_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("technicians.id"))

    maintenance_type: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(Text)
    cost: Mapped[float | None] = mapped_column(Float)
    performed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    equipment: Mapped["Equipment"] = relationship("Equipment", back_populates="maintenance_records")


# Alias for backwards compatibility
MaintenanceHistory = MaintenanceRecord
