"""
ClipoAI Backend — FastAPI Application Factory.

Creates and configures the FastAPI application with:
- CORS middleware
- Structured logging
- Prometheus metrics
- API routers
"""

from contextlib import asynccontextmanager

import structlog
import redis.asyncio as redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.config import settings

# Configure structured logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer() if settings.debug else structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(0),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Handle application startup and shutdown lifecycle events."""
    logger.info("ClipoAI backend starting", env=settings.app_env)
    
    # Initialize Rate Limiter
    redis_conn = redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_conn)
    
    yield
    
    logger.info("ClipoAI backend shutting down")
    await redis_conn.close()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    application = FastAPI(
        title=settings.app_name,
        description="Enterprise AI Video Processing Platform",
        version="0.1.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Prometheus metrics
    Instrumentator().instrument(application).expose(
        application, endpoint="/api/metrics", include_in_schema=False
    )

    # Routers
    application.include_router(health_router, prefix="/api")
    application.include_router(auth_router, prefix="/api/auth", tags=["auth"])

    return application


app = create_app()
