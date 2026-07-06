import re

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from app.config import settings
from app.models import Base


def _async_db_url(url: str) -> str:
    """Ensure the database URL uses the asyncpg driver for async engines.

    Railway injects DATABASE_URL as 'postgresql://...' (sync scheme), but
    create_async_engine requires 'postgresql+asyncpg://...'. This also handles
    'postgresql+psycopg://' and similar variants, converts 'sslmode'
    query param to 'ssl', and disables prepared statement cache for PgBouncer.
    """
    # asyncpg's connect() expects 'ssl' not 'sslmode' as a query parameter
    url = re.sub(r"sslmode=([^&]+)", r"ssl=\1", url)
    # Ensure asyncpg driver
    url = re.sub(r"^postgresql(?:\+[^+]+)?://", "postgresql+asyncpg://", url)
    # Disable prepared statement cache for PgBouncer compatibility
    if "statement_cache_size" not in url:
        url += ("&" if "?" in url else "?") + "statement_cache_size=0"
    return url


# Use psycopg_async driver (avoids PgBouncer + asyncpg prepared statement cache conflict)
engine = create_async_engine(
    _async_db_url(settings.database_url),
    echo=False,
    poolclass=NullPool,
    connect_args={"statement_cache_size": 0},
)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
