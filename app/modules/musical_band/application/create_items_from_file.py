from app.core.db import SessionDep
from app.modules.inventory.infrastructure.enrollment_adapter import (
    InventoryEnrollmentAdapter,
)
from app.modules.inventory.infrastructure.repository import InventoryRepository
from app.modules.inventory.schemas.request import InventoryItemRequest
from app.modules.inventory.schemas.response import ImportItemsResponse, ImportRowError
from app.modules.musical_band.domain.service import MusicalBandService


class CreateItemsMusicalBandFromFile:
    """Importación masiva restringida al tipo de inventario de banda."""

    allowed_type: str | None = "banda"

    def __init__(self, session: SessionDep):
        self._service = MusicalBandService(
            repository=InventoryRepository(session=session),
            enrollment=InventoryEnrollmentAdapter(session=session),
        )

    async def execute(
        self,
        valid_items: list[tuple[int, InventoryItemRequest]],
        parse_errors: list[ImportRowError],
    ) -> ImportItemsResponse:
        return await self._service.import_items(
            valid_items=valid_items,
            parse_errors=parse_errors,
            allowed_type=self.allowed_type,
        )
