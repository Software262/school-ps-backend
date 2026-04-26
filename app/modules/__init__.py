from fastapi import APIRouter

from app.modules.health.api.routes import router as health
from app.modules.musical_band.api.routes import router as musical_band

router = APIRouter(
    prefix="/api/v1",
)

router.include_router(health, prefix="/health", tags=["health"])
router.include_router(musical_band, prefix="/musical-band", tags=["musical-band"])
