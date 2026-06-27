"""
Health Check Endpoint.

Provides system health information including database and Redis connectivity.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)) -> dict:
    """
    Check the health of all services.

    Returns the status of:
    - API server
    - PostgreSQL database
    - Redis cache
    """
    health = {
        "status": "healthy",
        "service": "ClipoAI Backend",
        "checks": {},
    }

    # Check PostgreSQL
    try:
        await db.execute(text("SELECT 1"))
        health["checks"]["postgres"] = {"status": "healthy"}
    except Exception as e:
        health["status"] = "degraded"
        health["checks"]["postgres"] = {"status": "unhealthy", "error": str(e)}

    # Check Redis
    try:
        import redis.asyncio as aioredis

        from app.config import settings

        r = aioredis.from_url(settings.redis_url)
        await r.ping()
        await r.aclose()
        health["checks"]["redis"] = {"status": "healthy"}
    except Exception as e:
        health["status"] = "degraded"
        health["checks"]["redis"] = {"status": "unhealthy", "error": str(e)}

    return health
