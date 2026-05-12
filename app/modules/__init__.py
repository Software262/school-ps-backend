from fastapi import APIRouter

from app.modules.health.api.routes import router as health
from app.modules.inventory.api.routes import router as inventory
from app.modules.musical_band.api.routes import router as musical_band
from app.modules.principal.api.routes import router as principal

router = APIRouter(
    prefix="/api/v1",
)

router.include_router(health, prefix="/health", tags=["health"])
router.include_router(inventory, prefix="/inventory", tags=["inventory"])
router.include_router(musical_band, prefix="/musical-band", tags=["musical-band"])
router.include_router(principal, prefix="/principal", tags=["principal"])
