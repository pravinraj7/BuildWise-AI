"""
BuildWise AI — Schedules Router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from database import get_db
from models.schedule import Schedule, ScheduleStatus
from models.user import User
from services.jwt_service import get_current_user

router = APIRouter()


@router.get("/")
async def list_schedules(
    technician_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Schedule)
    if technician_id:
        query = query.where(Schedule.technician_id == technician_id)
    if status_filter:
        query = query.where(Schedule.status == status_filter)

    result = await db.execute(query.order_by(Schedule.scheduled_start.desc()))
    schedules = result.scalars().all()
    return {"data": schedules, "count": len(schedules)}


@router.get("/{schedule_id}")
async def get_schedule(
    schedule_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")
    return schedule
