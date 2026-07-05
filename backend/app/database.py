from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from app.config import settings
from app.models import Base


def _async_db_url(url: str) -> str:
    """Ensure the database URL uses the asyncpg driver for async engines.

    Railway injects DATABASE_URL as 'postgresql://...' but create_async_engine
    requires 'postgresql+asyncpg://...'. Auto-fix if the scheme is missing the driver.
    """
    if url.startswith("postgresql://") and "+" not in url.split("://")[0]:
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


# Use psycopg_async driver (avoids PgBouncer + asyncpg prepared statement cache conflict)
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
