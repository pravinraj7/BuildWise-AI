"""
BuildWise AI — Predictions Router
"""
from typing import Optional
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models.prediction import Prediction
from models.equipment import Equipment
from models.user import User
from services.jwt_service import get_current_user

router = APIRouter()


@router.get("")
async def list_predictions(
    equipment_id: Optional[str] = None,
    risk_level: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Prediction).order_by(Prediction.created_at.desc())
    if equipment_id:
        query = query.where(Prediction.equipment_id == equipment_id)
    if risk_level:
        query = query.where(Prediction.risk_level == risk_level)
    result = await db.execute(query.limit(50))
    predictions = result.scalars().all()
    return [
        {
            "id": p.id, "equipment_id": p.equipment_id, "model_name": p.model_name,
            "prediction_type": p.prediction_type, "failure_probability": p.failure_probability,
            "predicted_failure_date": p.predicted_failure_date.isoformat() if p.predicted_failure_date else None,
            "remaining_useful_life_days": p.remaining_useful_life_days,
            "health_score": p.health_score, "risk_level": p.risk_level,
            "recommended_action": p.recommended_action, "model_confidence": p.model_confidence,
            "created_at": p.created_at.isoformat(),
        }
        for p in predictions
    ]


@router.post("/run/{equipment_id}")
async def run_prediction(
    equipment_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Equipment).where(Equipment.id == equipment_id))
    equipment = result.scalar_one_or_none()
    if not equipment:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Equipment not found")

    background_tasks.add_task(_run_prediction_task, equipment_id)
    return {"message": "Prediction started", "equipment_id": equipment_id, "status": "processing"}


async def _run_prediction_task(equipment_id: str):
    try:
        from services.ml_service import predict_equipment_failure
        await predict_equipment_failure(equipment_id)
    except Exception as e:
        import structlog
        structlog.get_logger().error("Prediction failed", equipment_id=equipment_id, error=str(e))
