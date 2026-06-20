from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import analyze, clearance, closure, copilot, dashboard, health, intelligence, priority, resource
from app.core.config import get_settings
from app.core.logger import configure_logging, get_logger
from app.core.registry import model_registry
from app.database.client import mongo
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.request_id import RequestIdMiddleware

configure_logging()
logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    model_registry.load_models(settings)
    try:
        await mongo.connect(settings)
    except Exception as exc:
        logger.warning("MongoDB startup connection failed; continuing degraded: %s", exc)
    yield
    await mongo.close()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="FastAPI backend for GRIDLOCK / SENTINEL AI Traffic Intelligence Platform.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(RateLimitMiddleware)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(health.router, prefix=settings.api_v1_prefix)
app.include_router(closure.router, prefix=settings.api_v1_prefix)
app.include_router(priority.router, prefix=settings.api_v1_prefix)
app.include_router(clearance.router, prefix=settings.api_v1_prefix)
app.include_router(clearance.retrieve_router, prefix=settings.api_v1_prefix)
app.include_router(resource.router, prefix=settings.api_v1_prefix)
app.include_router(analyze.router, prefix=settings.api_v1_prefix)
app.include_router(copilot.router, prefix=settings.api_v1_prefix)
app.include_router(intelligence.router, prefix=settings.api_v1_prefix)
app.include_router(dashboard.router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root() -> dict:
    return {"service": settings.app_name, "docs": "/docs", "health": f"{settings.api_v1_prefix}/health"}
