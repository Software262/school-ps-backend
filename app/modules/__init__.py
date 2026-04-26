from fastapi import APIRouter

from app.modules.health.api.routes import router as health

router = APIRouter(
    prefix="/api/v1",
)

router.include_router(health, prefix="/health", tags=["health"])
