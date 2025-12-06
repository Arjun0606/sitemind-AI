"""
SiteMind Database Connection Management
Async database session handling for FastAPI
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config import settings
from models.database import Base


# Async engine for FastAPI
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

# Sync engine for migrations and scripts
sync_engine = create_engine(
    settings.database_sync_url,
    echo=settings.debug,
    pool_size=5,
    max_overflow=5,
    pool_pre_ping=True,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# Sync session factory (for migrations)
SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autoflush=False,
    autocommit=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI to get async database session
    
    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_async_session)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """
    Initialize database tables
    Call this on application startup
    """
    async with async_engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """
    Close database connections
    Call this on application shutdown
    """
    await async_engine.dispose()


def init_db_sync():
    """
    Initialize database tables (synchronous version)
    Useful for scripts and migrations
    """
    Base.metadata.create_all(bind=sync_engine)

