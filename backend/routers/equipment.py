"""
BuildWise AI — Equipment Router
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from models.equipment import Equipment, MaintenanceHistory, EquipmentStatus
from models.user import User
from services.jwt_service import get_current_user

router = APIRouter()


class CreateEquipmentRequest(BaseModel):
    building_id: str
    floor_id: Optional[str] = None
    name: str
    equipment_type: str
    model_number: Optional[str] = None
    serial_number: Optional[str] = None
    manufacturer: Optional[str] = None
    installation_date: Optional[datetime] = None
    is_critical: bool = False
    specifications: Optional[dict] = None


def equip_to_dict(e: Equipment) -> dict:
    return {
        "id": e.id, "building_id": e.building_id, "floor_id": e.floor_id,
        "name": e.name, "equipment_type": e.equipment_type,
        "model_number": e.model_number, "serial_number": e.serial_number,
        "manufacturer": e.manufacturer, "status": e.status.value,
        "health_score": e.health_score, "failure_probability": e.failure_probability,
        "remaining_useful_life_days": e.remaining_useful_life_days,
        "last_maintenance_date": e.last_maintenance_date.isoformat() if e.last_maintenance_date else None,
        "next_maintenance_date": e.next_maintenance_date.isoformat() if e.next_maintenance_date else None,
        "is_critical": e.is_critical, "sensor_data": e.sensor_data,
        "specifications": e.specifications, "created_at": e.created_at.isoformat(),
    }


@router.get("")
async def list_equipment(
    building_id: Optional[str] = None,
    equipment_type: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy.orm import selectinload
    query = select(Equipment).options(selectinload(Equipment.predictions))
    if building_id:
        query = query.where(Equipment.building_id == building_id)
    if equipment_type:
        query = query.where(Equipment.equipment_type == equipment_type)
    if status:
        query = query.where(Equipment.status == status)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
    result = await db.execute(query.offset((page - 1) * limit).limit(limit))
    equipment = result.scalars().all()
    return {"data": [equip_to_dict(e) for e in equipment], "total": total, "page": page}


@router.post("", status_code=201)
async def create_equipment(payload: CreateEquipmentRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    e = Equipment(**payload.model_dump())
    db.add(e)
    await db.flush()
    return equip_to_dict(e)


@router.get("/{equipment_id}")
async def get_equipment(equipment_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Equipment).where(Equipment.id == equipment_id))
    e = result.scalar_one_or_none()
    if not e:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equip_to_dict(e)


@router.patch("/{equipment_id}")
async def update_equipment(equipment_id: str, payload: dict, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Equipment).where(Equipment.id == equipment_id))
    e = result.scalar_one_or_none()
    if not e:
        raise HTTPException(status_code=404, detail="Equipment not found")
    allowed = {"health_score", "failure_probability", "status", "sensor_data", "next_maintenance_date", "remaining_useful_life_days"}
    for key, value in payload.items():
        if key in allowed:
            setattr(e, key, value)
    return equip_to_dict(e)


@router.get("/{equipment_id}/history")
async def get_maintenance_history(equipment_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(MaintenanceHistory)
        .where(MaintenanceHistory.equipment_id == equipment_id)
        .order_by(MaintenanceHistory.performed_at.desc())
    )
    history = result.scalars().all()
    return [
        {
            "id": h.id, "maintenance_type": h.maintenance_type, "description": h.description,
            "parts_replaced": h.parts_replaced, "total_cost": h.total_cost,
            "duration_hours": h.duration_hours, "health_score_before": h.health_score_before,
            "health_score_after": h.health_score_after, "performed_at": h.performed_at.isoformat(),
        }
        for h in history
    ]
