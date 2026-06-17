from app.core.db import SessionDep
from app.modules.inventory.domain.service import InventoryService
from app.modules.inventory.infrastructure.enrollment_adapter import (
    InventoryEnrollmentAdapter,
)
from app.modules.inventory.infrastructure.repository import InventoryRepository
from app.modules.inventory.schemas.request import InventoryItemRequest
from app.modules.inventory.schemas.response import ImportItemsResponse, ImportRowError


class CreateItemsInventoryFromFile:
    allowed_type: str | None = None

    def __init__(self, session: SessionDep):
        self.service = InventoryService(
            repository=InventoryRepository(session=session),
            enrollment=InventoryEnrollmentAdapter(session=session),
        )

    async def execute(
        self,
        valid_items: list[tuple[int, InventoryItemRequest]],
        parse_errors: list[ImportRowError],
    ) -> ImportItemsResponse:
        return await self.service.import_items(
            valid_items=valid_items, parse_errors=parse_errors
        )
