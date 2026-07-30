"""
BuildWise AI — Database Configuration & Session Management
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import event
import structlog

from config import settings

logger = structlog.get_logger()


class Base(DeclarativeBase):
    pass


def _make_engine(url: str):
    """Create async engine with appropriate pool settings for the given URL."""
    is_postgres = url.startswith("postgresql")
    kwargs = {"echo": settings.DEBUG}
    if is_postgres:
        kwargs.update({"pool_size": 10, "max_overflow": 20, "pool_pre_ping": True})
    return create_async_engine(url, **kwargs)


engine = _make_engine(settings.DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def init_db():
    """Initialize database schema with SQLite fallback if PostgreSQL is down."""
    global engine, AsyncSessionLocal
    # Import all models to ensure they're registered
    from models import (  # noqa: F401
        user, building, complaint, technician,
        schedule, equipment, prediction, knowledge,
        analytics, notification
    )
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("PostgreSQL database initialized successfully")
    except Exception as e:
        logger.warning(f"PostgreSQL connection failed ({e}). Falling back to SQLite async database.")
        sqlite_url = "sqlite+aiosqlite:///./buildwise.db"
        engine = create_async_engine(sqlite_url, echo=settings.DEBUG)
        AsyncSessionLocal = async_sessionmaker(
            bind=engine, class_=AsyncSession,
            expire_on_commit=False, autoflush=False, autocommit=False,
        )
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("SQLite database initialized successfully at ./buildwise.db")


async def get_db():
    """Dependency — yields an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
