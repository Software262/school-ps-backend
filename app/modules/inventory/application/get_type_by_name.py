from app.modules.inventory.domain.service import InventoryService
from app.modules.inventory.infrastructure.repository import InventoryRepository
from app.modules.inventory.infrastructure.enrollment_adapter import (
    InventoryEnrollmentAdapter,
)


class GetTypeByName:
    def __init__(self, session):
        self.service = InventoryService(
            repository=InventoryRepository(session=session),
            enrollment=InventoryEnrollmentAdapter(session=session),
        )

    async def execute(self, name: str):
        return await self.service.get_type_by_name(name=name)
