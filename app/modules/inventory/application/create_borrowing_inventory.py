from app.modules.inventory.domain.service import InventoryService
from app.modules.inventory.infrastructure.enrollment_adapter import (
    InventoryEnrollmentAdapter,
)
from app.modules.inventory.infrastructure.repository import InventoryRepository
from app.modules.inventory.schemas.request import CreateBorrowRequest


class CreateItemBorrowing:
    def __init__(self, session):
        self.service = InventoryService(
            repository=InventoryRepository(session=session),
            enrollment=InventoryEnrollmentAdapter(session=session),
        )

    async def execute(self, borrow_data: CreateBorrowRequest):
        return await self.service.create_borrow(borrow_data)
