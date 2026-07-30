"""
BuildWise AI — Buildings Router
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
import uuid
import shortuuid

from database import get_db
from models.building import Building, Floor, Department, Room
from models.user import User
from services.jwt_service import get_current_user

router = APIRouter()


class CreateBuildingRequest(BaseModel):
    name: str
    code: Optional[str] = None
    address: str = ""
    city: str = ""
    state: str = ""
    country: str = "India"
    total_floors: int = 1
    total_area_sqft: Optional[float] = None
    building_type: str = "office"
    manager_id: Optional[str] = None


@router.get("")
async def list_buildings(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Building).options(selectinload(Building.floors), selectinload(Building.departments)).where(Building.is_active == True)
    )
    buildings = result.scalars().all()
    return [
        {
            "id": b.id, "name": b.name, "code": b.code, "address": b.address,
            "city": b.city, "state": b.state, "building_type": b.building_type,
            "total_floors": b.total_floors, "health_score": b.health_score,
            "floors_count": len(b.floors), "departments_count": len(b.departments),
            "created_at": b.created_at.isoformat() if b.created_at else None,
        }
        for b in buildings
    ]


@router.post("", status_code=201)
async def create_building(payload: CreateBuildingRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    code = payload.code
    if not code:
        clean_prefix = "".join(c for c in payload.name if c.isalnum()).upper()[:6] or "BLD"
        code = f"{clean_prefix}-{shortuuid.ShortUUID().random(length=4).upper()}"

    existing = await db.execute(select(Building).where(Building.code == code))
    if existing.scalar_one_or_none():
        code = f"{code}-{shortuuid.ShortUUID().random(length=3).upper()}"

    building_data = payload.model_dump()
    building_data["code"] = code
    # Set default values for NOT NULL SQLite columns if they are None
    if not building_data.get("city"):
        building_data["city"] = ""
    if not building_data.get("state"):
        building_data["state"] = ""
    if not building_data.get("postal_code"):
        building_data["postal_code"] = ""
    
    building = Building(**building_data)
    db.add(building)
    await db.flush()

    # Auto-create floors
    for i in range(payload.total_floors):
        floor = Floor(building_id=building.id, floor_number=i, name=f"Floor {i}" if i > 0 else "Ground Floor")
        db.add(floor)

    await db.commit()
    return {"id": building.id, "name": building.name, "code": building.code}


@router.get("/{building_id}")
async def get_building(building_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Building)
        .options(selectinload(Building.floors).selectinload(Floor.rooms), selectinload(Building.departments))
        .where(Building.id == building_id)
    )
    b = result.scalar_one_or_none()
    if not b:
        raise HTTPException(status_code=404, detail="Building not found")
    return {
        "id": b.id, "name": b.name, "code": b.code, "address": b.address,
        "city": b.city, "state": b.state, "building_type": b.building_type,
        "total_floors": b.total_floors, "total_area_sqft": b.total_area_sqft,
        "health_score": b.health_score, "manager_id": b.manager_id,
        "floors": [{"id": f.id, "floor_number": f.floor_number, "floor_name": f.name, "rooms_count": len(f.rooms)} for f in b.floors],
        "departments": [{"id": d.id, "name": d.name, "code": d.code} for d in b.departments],
        "created_at": b.created_at.isoformat() if b.created_at else None,
    }


@router.delete("/{building_id}", status_code=204)
async def delete_building(building_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Building).where(Building.id == building_id))
    b = result.scalar_one_or_none()
    if not b:
        raise HTTPException(status_code=404, detail="Building not found")
    b.is_active = False
    await db.commit()
