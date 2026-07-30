import asyncio
import database
from database import init_db
from models.user import User, UserRole
from services.jwt_service import hash_password

async def run():
    await init_db()
    async with database.AsyncSessionLocal() as db:
        u = User(
            email="admin@buildwise.ai",
            username="admin",
            full_name="Admin User",
            hashed_password=hash_password("demo123"),
            role=UserRole.SUPER_ADMIN
        )
        db.add(u)
        await db.commit()
    print("USER CREATED SUCCESSFULLY")

if __name__ == "__main__":
    asyncio.run(run())
