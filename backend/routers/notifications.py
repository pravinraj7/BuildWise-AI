"""
BuildWise AI — Notifications Router
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from database import get_db
from models.notification import Notification
from models.user import User
from services.jwt_service import get_current_user

router = APIRouter()


@router.get("")
async def list_notifications(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(50)
    )
    notifications = result.scalars().all()
    return [
        {
            "id": n.id, "type": n.type.value, "title": n.title,
            "message": n.message, "link": n.link, "is_read": n.is_read,
            "created_at": n.created_at.isoformat(),
        }
        for n in notifications
    ]


@router.get("/unread-count")
async def unread_count(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    from sqlalchemy import func
    count = (await db.execute(
        select(func.count(Notification.id))
        .where(Notification.user_id == current_user.id, Notification.is_read == False)
    )).scalar()
    return {"unread_count": count}


@router.patch("/{notification_id}/read")
async def mark_as_read(notification_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Notification).where(Notification.id == notification_id, Notification.user_id == current_user.id))
    n = result.scalar_one_or_none()
    if n:
        n.is_read = True
        n.read_at = datetime.utcnow()
    return {"success": True}


@router.patch("/read-all")
async def mark_all_read(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Notification).where(Notification.user_id == current_user.id, Notification.is_read == False))
    notifications = result.scalars().all()
    now = datetime.utcnow()
    for n in notifications:
        n.is_read = True
        n.read_at = now
    return {"success": True, "marked_count": len(notifications)}
