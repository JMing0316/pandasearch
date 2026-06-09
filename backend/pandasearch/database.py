"""PostgreSQL database connection management."""

from contextlib import asynccontextmanager
from typing import Optional

import asyncpg

_pool: Optional[asyncpg.Pool] = None


async def init_db(db_url: Optional[str] = None) -> None:
    """Initialize database connection pool."""
    global _pool
    if _pool is not None:
        return

    from pandasearch.config import Settings
    settings = Settings()
    dsn = db_url or settings.DATABASE_URL

    _pool = await asyncpg.create_pool(
        dsn=dsn,
        min_size=5,
        max_size=20,
        command_timeout=60,
    )


@asynccontextmanager
async def get_connection(db_url: Optional[str] = None):
    """Get a database connection from the pool."""
    global _pool
    if _pool is None:
        await init_db(db_url)

    async with _pool.acquire() as conn:
        yield conn


async def close_db() -> None:
    """Close database connection pool."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
