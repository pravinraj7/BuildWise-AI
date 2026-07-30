"""
BuildWise AI — Authentication Router
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
import shortuuid

from database import get_db
from models.user import User, UserRole
from services.jwt_service import (
    hash_password, verify_password,
    create_access_token, get_current_user
)

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    password: str
    phone: str | None = None
    role: UserRole = UserRole.RESIDENT
    building_id: str | None = None
    department: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: str
    role: str
    phone: str | None
    avatar_url: str | None
    building_id: str | None
    department: str | None
    is_active: bool
    created_at: datetime


# ── Endpoints ─────────────────────────────────────────────────────────────────
@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check existing
    existing = await db.execute(
        select(User).where((User.email == payload.email) | (User.username == payload.username))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email or username already registered")

    user = User(
        email=payload.email,
        username=payload.username,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        phone=payload.phone,
        role=payload.role,
        building_id=payload.building_id,
        department=payload.department,
    )
    db.add(user)
    await db.flush()

    role_str = user.role.value if hasattr(user.role, "value") else str(user.role)
    token = create_access_token({"sub": user.id, "role": role_str})
    return TokenResponse(
        access_token=token,
        user={
            "id": user.id, "email": user.email, "username": user.username,
            "full_name": user.full_name, "role": role_str,
        }
    )


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    role_str = user.role.value if hasattr(user.role, "value") else str(user.role)
    token = create_access_token({"sub": user.id, "role": role_str})

    return TokenResponse(
        access_token=token,
        user={
            "id": user.id,
            "email": user.email,
            "username": getattr(user, "username", user.email.split("@")[0]),
            "full_name": user.full_name,
            "role": role_str,
            "phone": getattr(user, "phone", None),
            "avatar_url": getattr(user, "avatar_url", None),
        }
    )


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    role_str = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        role=role_str,
        phone=current_user.phone,
        avatar_url=current_user.avatar_url,
        building_id=current_user.building_id,
        department=current_user.department,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
    )


@router.put("/me", response_model=UserResponse)
async def update_me(
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    allowed = {"full_name", "phone", "avatar_url", "department"}
    for key, value in payload.items():
        if key in allowed:
            setattr(current_user, key, value)
    await db.flush()
    return await me(current_user)
