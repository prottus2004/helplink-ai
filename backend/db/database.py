from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from collections.abc import AsyncGenerator
import sys
import os

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DATABASE_URL

# Create the async engine
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# Create the async session factory
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Declarative base model
Base = declarative_base()

# Dependency provider for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Helper function to create all tables
async def create_all_tables():
    async with engine.begin() as conn:
        # Import models inside to avoid circular imports during startup
        import db.models as models
        await conn.run_sync(Base.metadata.create_all)
