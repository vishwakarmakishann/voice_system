from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

from .core.config import settings
from .core.logger import setup_logging, logger
from .core.db import get_db, get_redis
from .api import livekit, memory, auth
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from .core.rate_limit import limiter
setup_logging()

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(livekit.router, prefix="/livekit", tags=["LiveKit"])
app.include_router(memory.router, prefix="/memory", tags=["Memory"])
@app.on_event("startup")
async def startup_event():
    await logger.ainfo("application_starting", version=settings.VERSION)
    from .services.memory_service import init_qdrant
    await init_qdrant()
@app.get("/health")
async def health_check(
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    health_status = {
        "status": "ok",
        "services": {
            "postgres": "down",
            "redis": "down"
        }
    }
    
    # Check Postgres
    try:
        await db.execute(text("SELECT 1"))
        health_status["services"]["postgres"] = "up"
    except Exception as e:
        await logger.aerror("postgres_health_check_failed", error=str(e))
        
    # Check Redis
    try:
        await redis_client.ping()
        health_status["services"]["redis"] = "up"
    except Exception as e:
        await logger.aerror("redis_health_check_failed", error=str(e))
        
    if health_status["services"]["postgres"] != "up" or health_status["services"]["redis"] != "up":
        health_status["status"] = "degraded"
        
    return health_status
