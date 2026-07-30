"""
BuildWise AI — Complaints Router (Full CRUD + AI trigger)
"""
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from database import get_db
from models.complaint import Complaint, ComplaintAttachment, ComplaintTimeline, ComplaintStatus, PriorityLevel, ComplaintCategory
from models.user import User
from services.jwt_service import get_current_user

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────────────
class CreateComplaintRequest(BaseModel):
    title: str
    description: str
    building_id: str
    floor_id: Optional[str] = None
    room_id: Optional[str] = None
    department_id: Optional[str] = None
    location_description: Optional[str] = None
    category: ComplaintCategory = ComplaintCategory.GENERAL


class UpdateComplaintRequest(BaseModel):
    status: Optional[ComplaintStatus] = None
    priority: Optional[PriorityLevel] = None
    assigned_technician_id: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    estimated_labor_cost: Optional[float] = None
    estimated_material_cost: Optional[float] = None
    estimated_total_cost: Optional[float] = None
    estimated_duration_hours: Optional[float] = None
    ai_diagnosis: Optional[str] = None
    ai_suggested_repair: Optional[str] = None


def generate_ticket_number() -> str:
    ts = datetime.utcnow().strftime("%Y%m%d")
    rand = str(uuid.uuid4())[:6].upper()
    return f"BW-{ts}-{rand}"


def complaint_to_dict(c: Complaint) -> dict:
    # Check loaded attributes in __dict__ to avoid lazy loading trigger in async context
    attachments = c.__dict__.get("attachments") or []
    timeline = c.__dict__.get("timeline") or []

    return {
        "id": c.id,
        "ticket_number": c.ticket_number,
        "title": c.title,
        "description": c.description,
        "status": c.status.value if c.status else None,
        "priority": c.priority.value if c.priority else None,
        "category": c.category.value if c.category else None,
        "building_id": c.building_id,
        "floor_id": c.floor_id,
        "room_id": c.room_id,
        "department_id": c.department_id,
        "location_description": c.location_description,
        "requester_id": c.requester_id,
        "assigned_technician_id": c.assigned_technician_id,
        "ai_diagnosis": c.ai_diagnosis,
        "ai_suggested_repair": c.ai_suggested_repair,
        "ai_suggested_parts": c.ai_suggested_parts,
        "ai_confidence_score": c.ai_confidence_score,
        "ai_processed_at": c.ai_processed_at.isoformat() if c.ai_processed_at else None,
        "estimated_labor_cost": c.estimated_labor_cost,
        "estimated_material_cost": c.estimated_material_cost,
        "estimated_total_cost": c.estimated_total_cost,
        "estimated_duration_hours": c.estimated_duration_hours,
        "actual_cost": c.actual_cost,
        "scheduled_at": c.scheduled_at.isoformat() if c.scheduled_at else None,
        "completed_at": c.completed_at.isoformat() if c.completed_at else None,
        "is_emergency": c.is_emergency,
        "requires_evacuation": c.requires_evacuation,
        "resolution_rating": c.resolution_rating,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
        "attachments": [
            {"id": a.id, "file_type": a.file_type, "file_name": a.file_name,
             "file_url": a.file_url, "cv_analysis": a.cv_analysis}
            for a in attachments
        ],
        "timeline": [
            {"id": t.id, "action": t.action, "description": t.description,
             "actor_name": t.actor_name, "actor_type": t.actor_type,
             "created_at": t.created_at.isoformat() if t.created_at else None}
            for t in timeline
        ],
    }


@router.get("")
async def list_complaints(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    building_id: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Complaint).options(
        selectinload(Complaint.attachments),
        selectinload(Complaint.timeline),
    )

    filters = []
    if status:
        filters.append(Complaint.status == status)
    if priority:
        filters.append(Complaint.priority == priority)
    if category:
        filters.append(Complaint.category == category)
    if building_id:
        filters.append(Complaint.building_id == building_id)
    if search:
        filters.append(
            or_(
                Complaint.title.ilike(f"%{search}%"),
                Complaint.description.ilike(f"%{search}%"),
                Complaint.ticket_number.ilike(f"%{search}%"),
            )
        )

    # Residents see only their own complaints
    from models.user import UserRole
    if current_user.role == UserRole.RESIDENT:
        filters.append(Complaint.requester_id == current_user.id)

    if filters:
        query = query.where(and_(*filters))

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    # Paginate
    query = query.order_by(Complaint.created_at.desc()).offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    complaints = result.scalars().all()

    return {
        "data": [complaint_to_dict(c) for c in complaints],
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
    }


@router.post("", status_code=201)
async def create_complaint(
    payload: CreateComplaintRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    complaint = Complaint(
        ticket_number=generate_ticket_number(),
        title=payload.title,
        description=payload.description,
        building_id=payload.building_id,
        floor_id=payload.floor_id,
        room_id=payload.room_id,
        department_id=payload.department_id,
        location_description=payload.location_description,
        category=payload.category,
        requester_id=current_user.id,
        status=ComplaintStatus.SUBMITTED,
    )
    db.add(complaint)
    await db.flush()

    # Add initial timeline entry
    timeline = ComplaintTimeline(
        complaint_id=complaint.id,
        action="SUBMITTED",
        description=f"Complaint submitted by {current_user.full_name}",
        actor_id=current_user.id,
        actor_name=current_user.full_name,
        actor_type="user",
    )
    db.add(timeline)
    await db.flush()

    # Trigger AI processing in background
    background_tasks.add_task(trigger_ai_processing, complaint.id)

    return complaint_to_dict(complaint)


@router.get("/{complaint_id}")
async def get_complaint(
    complaint_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Complaint)
        .options(selectinload(Complaint.attachments), selectinload(Complaint.timeline))
        .where(Complaint.id == complaint_id)
    )
    complaint = result.scalar_one_or_none()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint_to_dict(complaint)


@router.patch("/{complaint_id}")
async def update_complaint(
    complaint_id: str,
    payload: UpdateComplaintRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Complaint)
        .options(selectinload(Complaint.attachments), selectinload(Complaint.timeline))
        .where(Complaint.id == complaint_id)
    )
    complaint = result.scalar_one_or_none()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    update_data = payload.model_dump(exclude_none=True)
    for key, value in update_data.items():
        setattr(complaint, key, value)

    if payload.status == ComplaintStatus.COMPLETED:
        complaint.completed_at = datetime.utcnow()

    # Add timeline entry
    timeline = ComplaintTimeline(
        complaint_id=complaint.id,
        action="UPDATED",
        description=f"Complaint updated: {', '.join(update_data.keys())}",
        actor_id=current_user.id,
        actor_name=current_user.full_name,
        actor_type="user",
    )
    db.add(timeline)

    return complaint_to_dict(complaint)


@router.delete("/{complaint_id}", status_code=204)
async def delete_complaint(
    complaint_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Complaint).where(Complaint.id == complaint_id))
    complaint = result.scalar_one_or_none()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    await db.delete(complaint)


@router.get("/stats/summary")
async def complaint_stats(
    building_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    base = select(func.count(Complaint.id))
    if building_id:
        base = base.where(Complaint.building_id == building_id)

    total = (await db.execute(base)).scalar()
    pending = (await db.execute(base.where(Complaint.status.in_(["submitted", "ai_processing", "diagnosed", "assigned"])))).scalar()
    in_progress = (await db.execute(base.where(Complaint.status == "in_progress"))).scalar()
    resolved = (await db.execute(base.where(Complaint.status == "completed"))).scalar()
    critical = (await db.execute(base.where(Complaint.priority.in_(["critical", "emergency"])))).scalar()
    emergency = (await db.execute(base.where(Complaint.is_emergency == True))).scalar()

    return {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "resolved": resolved,
        "critical": critical,
        "emergency": emergency,
        "resolution_rate": round((resolved / total * 100) if total else 0, 1),
    }


async def trigger_ai_processing(complaint_id: str):
    """Background task: trigger the AI agent workflow for a complaint."""
    try:
        from services.ai_orchestrator import process_complaint_with_agents
        await process_complaint_with_agents(complaint_id)
    except Exception as e:
        import structlog
        structlog.get_logger().error("AI processing failed", complaint_id=complaint_id, error=str(e))
