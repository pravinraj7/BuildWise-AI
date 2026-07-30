"""
BuildWise AI — Seed Users Script (SQLite direct)
Creates one demo user for every role.
"""
import asyncio
import sys
import os

# Force SQLite — bypass PostgreSQL
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./buildwise.db")

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from models.user import User, UserRole
from services.jwt_service import hash_password
from database import Base

SEED_USERS = [
    {"email": "superadmin@buildwise.ai", "username": "superadmin",      "full_name": "Super Admin",       "password": "Admin@123", "role": UserRole.SUPER_ADMIN},
    {"email": "admin@buildwise.ai",      "username": "admin",           "full_name": "Admin User",         "password": "Admin@123", "role": UserRole.BUILDING_ADMIN},
    {"email": "facility@buildwise.ai",   "username": "facilitymanager", "full_name": "Facility Manager",   "password": "Admin@123", "role": UserRole.FACILITY_MANAGER},
    {"email": "manager@buildwise.ai",    "username": "manager",         "full_name": "Manager User",       "password": "Admin@123", "role": UserRole.FACILITY_MANAGER},
    {"email": "technician@buildwise.ai", "username": "technician",      "full_name": "Technician User",    "password": "Admin@123", "role": UserRole.TECHNICIAN},
    {"email": "resident@buildwise.ai",   "username": "resident",        "full_name": "Resident User",      "password": "Admin@123", "role": UserRole.RESIDENT},
]


async def seed():
    sqlite_url = "sqlite+aiosqlite:///./buildwise.db"
    engine = create_async_engine(sqlite_url, echo=False)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    # Import all models so tables are registered
    from models import (  # noqa: F401
        user, building, complaint, technician,
        schedule, equipment, prediction, knowledge,
        analytics, notification
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        from sqlalchemy import select
        for data in SEED_USERS:
            res = await session.execute(
                select(User).where((User.email == data["email"]) | (User.username == data["username"]))
            )
            user_obj = res.scalar_one_or_none()
            if user_obj:
                user_obj.hashed_password = hash_password(data["password"])
                user_obj.role = data["role"]
                user_obj.is_active = True
                print(f"  [UPDATED] {data['role'].value:20s}  {data['email']}")
                continue
            u = User(
                email=data["email"],
                username=data["username"],
                full_name=data["full_name"],
                hashed_password=hash_password(data["password"]),
                role=data["role"],
                is_active=True,
                is_verified=True,
            )
            session.add(u)
            print(f"  [OK]   {data['role'].value:20s}  {data['email']}")
        await session.commit()

    await engine.dispose()
    print("\nAll users seeded successfully!")
    print("\nPassword for ALL accounts: Admin@123")


if __name__ == "__main__":
    asyncio.run(seed())
