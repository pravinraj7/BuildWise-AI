"""
BuildWise AI — Failure Prediction Models
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class FailurePrediction(Base):
    __tablename__ = "failure_predictions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    equipment_id: Mapped[str] = mapped_column(String(36), ForeignKey("equipment.id"), nullable=False)

    failure_probability: Mapped[float] = mapped_column(Float, nullable=False)
    predicted_failure_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    risk_level: Mapped[str] = mapped_column(String(20), default="low")

    top_failure_factors: Mapped[list | None] = mapped_column(JSON)
    recommendations: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    equipment: Mapped["Equipment"] = relationship("Equipment", back_populates="predictions")

    @property
    def model_name(self) -> str:
        return "xgboost_failure_predictor"

    @property
    def prediction_type(self) -> str:
        return "failure"

    @property
    def remaining_useful_life_days(self) -> int:
        if self.predicted_failure_date:
            failure_date = self.predicted_failure_date.replace(tzinfo=None)
            delta = failure_date - datetime.utcnow()
            return max(0, delta.days)
        return 365

    @property
    def health_score(self) -> float:
        return round((1.0 - self.failure_probability) * 100.0, 1)

    @property
    def recommended_action(self) -> str:
        return self.recommendations or ""

    @property
    def model_confidence(self) -> float:
        return 0.85


# Alias for compatibility
Prediction = FailurePrediction
