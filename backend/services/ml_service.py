"""
BuildWise AI — ML Service (XGBoost + LightGBM + Isolation Forest)
"""
import os
import asyncio
import numpy as np
import structlog
from datetime import datetime, timedelta
from typing import Optional

logger = structlog.get_logger()

# Models are saved in backend/models/ directory (alongside SQLAlchemy model files)
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")


def _load_model(model_name: str):
    """Load a saved ML model."""
    import joblib
    path = os.path.join(MODEL_DIR, f"{model_name}.joblib")
    if os.path.exists(path):
        return joblib.load(path)
    return None


async def predict_equipment_failure(equipment_id: str) -> dict:
    """Run failure prediction for equipment using XGBoost/LightGBM."""
    from database import AsyncSessionLocal
    from models.equipment import Equipment
    from models.prediction import Prediction
    from models.equipment import MaintenanceHistory
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Equipment).where(Equipment.id == equipment_id))
        equipment = result.scalar_one_or_none()
        if not equipment:
            return {}

        # Get maintenance history
        hist_result = await db.execute(
            select(MaintenanceHistory)
            .where(MaintenanceHistory.equipment_id == equipment_id)
            .order_by(MaintenanceHistory.performed_at.desc())
            .limit(10)
        )
        history = hist_result.scalars().all()

        # Feature engineering
        features = _extract_features(equipment, history)
        
        # Run prediction
        failure_prob, risk_level, rul_days = _run_ml_prediction(features, equipment.equipment_type)

        # Save prediction
        prediction = Prediction(
            equipment_id=equipment_id,
            failure_probability=failure_prob,
            predicted_failure_date=datetime.utcnow() + timedelta(days=rul_days) if rul_days else None,
            risk_level=risk_level,
            recommendations=_get_recommendation(failure_prob, risk_level),
            top_failure_factors=["temperature", "vibration"] if failure_prob >= 0.4 else [],
        )
        db.add(prediction)

        # Update equipment
        equipment.failure_probability = failure_prob
        equipment.remaining_useful_life_days = rul_days
        if failure_prob > 0.8:
            from models.equipment import EquipmentStatus
            equipment.status = EquipmentStatus.DEGRADED

        await db.commit()
        logger.info("Prediction complete", equipment_id=equipment_id, failure_prob=failure_prob)

    return {
        "equipment_id": equipment_id,
        "failure_probability": failure_prob,
        "risk_level": risk_level,
        "remaining_useful_life_days": rul_days,
    }


def _extract_features(equipment, history: list) -> dict:
    """Extract ML features from equipment data."""
    now = datetime.utcnow()
    
    days_since_install = 0
    if equipment.installation_date:
        days_since_install = (now - equipment.installation_date).days

    days_since_maintenance = 999
    if equipment.last_maintenance_date:
        days_since_maintenance = (now - equipment.last_maintenance_date).days

    maintenance_count = len(history)
    total_cost = sum(h.total_cost or 0 for h in history)
    avg_duration = np.mean([h.duration_hours or 0 for h in history]) if history else 0

    return {
        "age_days": days_since_install,
        "days_since_maintenance": days_since_maintenance,
        "maintenance_count": maintenance_count,
        "total_maintenance_cost": total_cost,
        "avg_repair_duration": float(avg_duration),
        "current_health_score": equipment.health_score,
        "is_critical": int(equipment.is_critical),
        "equipment_type_encoded": _encode_equipment_type(equipment.equipment_type),
    }


def _run_ml_prediction(features: dict, equipment_type: str) -> tuple:
    """Run prediction — uses saved model or rule-based fallback."""
    model = _load_model(f"failure_predictor_{equipment_type}")
    if model is None:
        model = _load_model("failure_predictor_generic")

    if model is not None:
        try:
            X = np.array([[
                features["age_days"],
                features["days_since_maintenance"],
                features["maintenance_count"],
                features["total_maintenance_cost"],
                features["avg_repair_duration"],
                features["current_health_score"],
                features["is_critical"],
                features["equipment_type_encoded"],
            ]])
            failure_prob = float(model.predict_proba(X)[0][1])
        except Exception as e:
            logger.warning(f"Model prediction failed: {e}, using rule-based")
            failure_prob = _rule_based_failure_prob(features)
    else:
        failure_prob = _rule_based_failure_prob(features)

    # Determine risk level
    if failure_prob >= 0.8:
        risk_level = "critical"
    elif failure_prob >= 0.6:
        risk_level = "high"
    elif failure_prob >= 0.35:
        risk_level = "medium"
    else:
        risk_level = "low"

    # Remaining useful life estimate
    rul_days = int((1 - failure_prob) * 180)  # 0-180 days

    return failure_prob, risk_level, rul_days


def _rule_based_failure_prob(features: dict) -> float:
    """Rule-based failure probability when ML model unavailable."""
    score = 0.0
    health = features.get("current_health_score", 100.0)
    age = features.get("age_days", 0)
    days_since = features.get("days_since_maintenance", 0)
    count = features.get("maintenance_count", 0)

    score += max(0, (100 - health) / 100) * 0.4
    score += min(1.0, age / 3650) * 0.2  # 10 year lifespan
    score += min(1.0, days_since / 365) * 0.25
    score += min(1.0, count / 10) * 0.15

    return round(min(0.99, max(0.01, score)), 3)


def _encode_equipment_type(equipment_type: str) -> int:
    types = ["elevator", "ac", "generator", "pump", "electrical_panel", "hvac", "boiler", "other"]
    return types.index(equipment_type) if equipment_type in types else 7


def _get_recommendation(failure_prob: float, risk_level: str) -> str:
    if risk_level == "critical":
        return "URGENT: Schedule immediate inspection and preventive maintenance. Consider temporary shutdown."
    elif risk_level == "high":
        return "Schedule maintenance within 7 days. Monitor closely for anomalies."
    elif risk_level == "medium":
        return "Schedule maintenance within 30 days. Increase monitoring frequency."
    else:
        return "Equipment operating normally. Continue standard maintenance schedule."
