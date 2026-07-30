"""
BuildWise AI — Analytics Router
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, extract

from database import get_db
from models.complaint import Complaint, ComplaintStatus, PriorityLevel, ComplaintCategory
from models.technician import Technician
from models.building import Building
from models.equipment import Equipment
from models.user import User
from services.jwt_service import get_current_user

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_analytics(
    building_id: Optional[str] = None,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    since = datetime.utcnow() - timedelta(days=days)
    base_filter = [Complaint.created_at >= since]
    if building_id:
        base_filter.append(Complaint.building_id == building_id)

    # KPIs
    total = (await db.execute(select(func.count(Complaint.id)).where(*base_filter))).scalar()
    resolved = (await db.execute(select(func.count(Complaint.id)).where(*base_filter, Complaint.status == "completed"))).scalar()
    pending = (await db.execute(select(func.count(Complaint.id)).where(*base_filter, Complaint.status.in_(["submitted", "ai_processing", "diagnosed", "assigned"])))).scalar()
    critical = (await db.execute(select(func.count(Complaint.id)).where(*base_filter, Complaint.priority.in_(["critical", "emergency"])))).scalar()
    in_progress = (await db.execute(select(func.count(Complaint.id)).where(*base_filter, Complaint.status == "in_progress"))).scalar()

    # Total cost
    total_cost = (await db.execute(select(func.sum(Complaint.actual_cost)).where(*base_filter))).scalar() or 0

    # Avg resolution time (compute in Python for SQLite compatibility)
    resolved_times_result = await db.execute(
        select(Complaint.created_at, Complaint.completed_at)
        .where(*base_filter, Complaint.completed_at.isnot(None))
    )
    resolved_times = resolved_times_result.all()
    if resolved_times:
        avg_resolution_hours = sum(
            (row[1] - row[0]).total_seconds() / 3600 for row in resolved_times
        ) / len(resolved_times)
    else:
        avg_resolution_hours = 0

    # Building health scores
    buildings_result = await db.execute(select(Building).where(Building.is_active == True))
    buildings = buildings_result.scalars().all()
    avg_health_score = sum(b.health_score for b in buildings) / len(buildings) if buildings else 100.0

    # Active technicians
    active_tech = (await db.execute(select(func.count(Technician.id)).where(Technician.is_active == True, Technician.status == "available"))).scalar()

    # Category breakdown
    cat_result = await db.execute(
        select(Complaint.category, func.count(Complaint.id))
        .where(*base_filter)
        .group_by(Complaint.category)
    )
    by_category = {row[0]: row[1] for row in cat_result.all()}

    # Priority breakdown
    pri_result = await db.execute(
        select(Complaint.priority, func.count(Complaint.id))
        .where(*base_filter)
        .group_by(Complaint.priority)
    )
    by_priority = {row[0]: row[1] for row in pri_result.all()}

    # Trend - complaints per day
    trend_result = await db.execute(
        select(
            func.date(Complaint.created_at).label("day"),
            func.count(Complaint.id).label("count")
        )
        .where(*base_filter)
        .group_by(func.date(Complaint.created_at))
        .order_by(func.date(Complaint.created_at))
    )
    trend = [{"date": str(row[0])[:10], "count": row[1]} for row in trend_result.all()]

    return {
        "kpis": {
            "total_complaints": total,
            "resolved": resolved,
            "pending": pending,
            "in_progress": in_progress,
            "critical": critical,
            "resolution_rate": round((resolved / total * 100) if total else 0, 1),
            "total_maintenance_cost": round(total_cost, 2),
            "avg_resolution_hours": round(avg_resolution_hours, 1),
            "building_health_score": round(avg_health_score, 1),
            "active_technicians": active_tech,
        },
        "by_category": by_category,
        "by_priority": by_priority,
        "trend": trend,
        "days": days,
    }


@router.get("/technician-performance")
async def get_technician_performance(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Technician).where(Technician.is_active == True).order_by(Technician.performance_score.desc()).limit(20)
    )
    technicians = result.scalars().all()
    return [
        {
            "id": t.id, "name": t.full_name, "rating": t.rating,
            "total_jobs": t.total_jobs, "completed_jobs": t.completed_jobs,
            "performance_score": t.performance_score,
            "avg_resolution_time": t.avg_resolution_time_hours,
            "status": t.status.value, "specialization": t.specialization,
        }
        for t in technicians
    ]


@router.get("/building-health")
async def get_building_health(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Building).where(Building.is_active == True))
    buildings = result.scalars().all()
    return [
        {"id": b.id, "name": b.name, "code": b.code, "health_score": b.health_score, "building_type": b.building_type}
        for b in buildings
    ]


@router.get("/equipment-risk")
async def get_equipment_risk(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Equipment).options(selectinload(Equipment.predictions))
    )
    equipment = result.scalars().all()
    
    # Filter and sort in Python to support SQLAlchemy properties
    high_risk_equip = [e for e in equipment if e.failure_probability > 0.3]
    high_risk_equip.sort(key=lambda e: e.failure_probability, reverse=True)
    
    return [
        {
            "id": e.id, "name": e.name, "equipment_type": e.equipment_type,
            "health_score": e.health_score, "failure_probability": e.failure_probability,
            "remaining_useful_life_days": e.remaining_useful_life_days,
            "status": e.status.value, "building_id": e.building_id,
        }
        for e in high_risk_equip[:10]
    ]
