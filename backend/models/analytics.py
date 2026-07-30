"""
BuildWise AI — Analytics & Snapshots Models
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Float, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class AnalyticsSnapshot(Base):
    __tablename__ = "analytics_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    period: Mapped[str] = mapped_column(String(50), default="daily")
    total_complaints: Mapped[int] = mapped_column(default=0)
    resolved_complaints: Mapped[int] = mapped_column(default=0)

    avg_resolution_time_hours: Mapped[float] = mapped_column(Float, default=0.0)
    total_cost: Mapped[float] = mapped_column(Float, default=0.0)
    customer_satisfaction_score: Mapped[float] = mapped_column(Float, default=0.0)

    metrics_by_category: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
