import re

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from app.config import settings
from app.models import Base


def _async_db_url(url: str) -> str:
    """Ensure the database URL uses the psycopg async driver.

    Railway injects DATABASE_URL as 'postgresql://...' (sync scheme), but
    create_async_engine requires 'postgresql+psycopg://...' for psycopg 3's
    async mode. psycopg 3 handles PgBouncer gracefully (no prepared statement
    cache conflict like asyncpg).
    """
    # psycopg supports sslmode natively, no need to convert
    return re.sub(r"^postgresql(?:\+[^+]+)?://", "postgresql+psycopg://", url)


engine = create_async_engine(
    _async_db_url(settings.database_url),
    echo=False,
    poolclass=NullPool,
)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
