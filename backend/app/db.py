import redis.asyncio as aioredis
from neo4j import AsyncGraphDatabase
from qdrant_client import AsyncQdrantClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings


class Clients:
    """One shared client per database, created at startup, closed at shutdown."""

    def __init__(self) -> None:
        self.pg = create_async_engine(settings.postgres_url, pool_pre_ping=True)
        self.neo4j = AsyncGraphDatabase.driver(
            settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password)
        )
        self.qdrant = AsyncQdrantClient(host=settings.qdrant_host, port=settings.qdrant_http_port)
        self.redis = aioredis.Redis(host=settings.redis_host, port=settings.redis_port)

    async def close(self) -> None:
        await self.pg.dispose()
        await self.neo4j.close()
        await self.qdrant.close()
        await self.redis.aclose()


async def check_all(c: Clients) -> dict[str, str]:
    """Ping every database; never crash, report each result."""
    results: dict[str, str] = {}

    async def run(name, coro):
        try:
            await coro
            results[name] = "ok"
        except Exception as e:  # report, don't crash the health check
            results[name] = f"error: {type(e).__name__}: {e}"

    async def ping_postgres():
        async with c.pg.connect() as conn:
            await conn.execute(text("SELECT 1"))

    await run("postgres", ping_postgres())
    await run("neo4j", c.neo4j.verify_connectivity())
    await run("qdrant", c.qdrant.get_collections())
    await run("redis", c.redis.ping())
    return results
