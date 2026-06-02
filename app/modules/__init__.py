from fastapi import APIRouter

from app.modules.classroom.api.routes import router as classroom
from app.modules.enrollment.api.routes import router as enrollment
from app.modules.health.api.routes import router as health
from app.modules.inventory.api.routes import router as inventory
from app.modules.musical_band.api.routes import router as musical_band
from app.modules.principal.api.routes import router as principal
from app.modules.tests.api.routes import router as tests
from app.modules.tuition.api.routes import router as tuition
from app.modules.cafeteria.api.routes import router as cafeteria
from app.modules.chess.api.routes import router as chess
from app.modules.sports.api.routes import router as sports

router = APIRouter(
    prefix="/api/v1",
)

router.include_router(health, prefix="/health", tags=["health"])
router.include_router(inventory, prefix="/inventory", tags=["inventory"])
router.include_router(musical_band, prefix="/musical-band", tags=["musical-band"])
router.include_router(enrollment, prefix="/enrollment", tags=["enrollment"])
router.include_router(principal, prefix="/principal", tags=["principal"])
router.include_router(tests, prefix="/tests", tags=["tests"])
router.include_router(tuition, prefix="/tuition", tags=["tuition"])
router.include_router(classroom, prefix="/classroom", tags=["classroom"])
router.include_router(cafeteria, prefix="/cafeteria", tags=["cafeteria"])
router.include_router(chess, prefix="/chess", tags=["chess"])
router.include_router(sports, prefix="/sports", tags=["sports"])
