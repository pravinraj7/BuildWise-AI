"""
BuildWise AI — Technicians Router
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel

from database import get_db
from models.technician import Technician, TechnicianStatus
from models.user import User
from services.jwt_service import get_current_user

router = APIRouter()


class CreateTechnicianRequest(BaseModel):
    employee_id: str
    full_name: str
    email: str
    phone: str
    skills: Optional[List[str]] = []
    certifications: Optional[List[str]] = []
    experience_years: int = 0
    specialization: Optional[str] = None
    assigned_building_id: Optional[str] = None
    shift_start: Optional[str] = "09:00"
    shift_end: Optional[str] = "18:00"
    work_days: Optional[List[str]] = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    max_concurrent_jobs: int = 3


def tech_to_dict(t: Technician) -> dict:
    return {
        "id": t.id,
        "employee_id": t.employee_id,
        "full_name": t.full_name,
        "email": t.email,
        "phone": t.phone,
        "avatar_url": t.avatar_url,
        "skills": t.skills or [],
        "certifications": t.certifications or [],
        "experience_years": t.experience_years,
        "specialization": t.specialization,
        "status": t.status.value,
        "current_location": t.current_location,
        "assigned_building_id": t.assigned_building_id,
        "rating": t.rating,
        "total_jobs": t.total_jobs,
        "completed_jobs": t.completed_jobs,
        "avg_resolution_time_hours": t.avg_resolution_time_hours,
        "performance_score": t.performance_score,
        "shift_start": t.shift_start,
        "shift_end": t.shift_end,
        "work_days": t.work_days or [],
        "current_workload": t.current_workload,
        "max_concurrent_jobs": t.max_concurrent_jobs,
        "is_active": t.is_active,
        "created_at": t.created_at.isoformat(),
    }


@router.get("")
async def list_technicians(
    status: Optional[str] = None,
    skill: Optional[str] = None,
    building_id: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Technician).where(Technician.is_active == True)
    if status:
        try:
            query = query.where(Technician.status == TechnicianStatus(status))
        except ValueError:
            pass  # ignore invalid status values
    if building_id:
        query = query.where(Technician.assigned_building_id == building_id)
    if search:
        query = query.where(
            Technician.full_name.ilike(f"%{search}%") | Technician.email.ilike(f"%{search}%")
        )

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    technicians = result.scalars().all()

    return {"data": [tech_to_dict(t) for t in technicians], "total": total, "page": page, "limit": limit}


@router.post("", status_code=201)
async def create_technician(
    payload: CreateTechnicianRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = await db.execute(
        select(Technician).where(
            (Technician.employee_id == payload.employee_id) | (Technician.email == payload.email)
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Technician with this employee ID or email already exists")

    data = payload.model_dump()
    technician = Technician(
        employee_id=data["employee_id"],
        full_name=data["full_name"],
        email=data["email"],
        phone=data["phone"],
        skills=data.get("skills", []),
        certifications=data.get("certifications", []),
        experience_years=data.get("experience_years", 0),
        specialization=data.get("specialization"),
        assigned_building_id=data.get("assigned_building_id"),
        shift_start=data.get("shift_start", "09:00"),
        shift_end=data.get("shift_end", "18:00"),
        work_days=data.get("work_days", ["Mon", "Tue", "Wed", "Thu", "Fri"]),
        max_concurrent_jobs=data.get("max_concurrent_jobs", 3),
    )
    db.add(technician)
    await db.flush()
    await db.commit()
    return tech_to_dict(technician)


@router.get("/available")
async def get_available_technicians(
    skill: Optional[str] = None,
    building_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Technician).where(
        Technician.is_active == True,
        Technician.status == TechnicianStatus.AVAILABLE,
        Technician.current_workload < Technician.max_concurrent_jobs,
    )
    if building_id:
        query = query.where(Technician.assigned_building_id == building_id)

    result = await db.execute(query)
    technicians = result.scalars().all()

    if skill:
        technicians = [t for t in technicians if t.skills and skill in t.skills]

    return [tech_to_dict(t) for t in technicians]


@router.get("/{technician_id}")
async def get_technician(technician_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Technician).where(Technician.id == technician_id))
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Technician not found")
    return tech_to_dict(t)


@router.patch("/{technician_id}")
async def update_technician(
    technician_id: str,
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Technician).where(Technician.id == technician_id))
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Technician not found")
    allowed = {"status", "current_location", "skills", "rating", "shift_start", "shift_end"}
    for key, value in payload.items():
        if key in allowed:
            setattr(t, key, value)
    return tech_to_dict(t)
