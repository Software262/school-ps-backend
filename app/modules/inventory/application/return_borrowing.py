from app.modules.inventory.domain.service import InventoryService
from app.modules.inventory.infrastructure.repository import InventoryRepository
from app.modules.inventory.schemas.request import ReturnBorrowRequest


class ReturnBorrowing:
    def __init__(self, session):
        self.repository = InventoryRepository(session=session)
        self.service = InventoryService(repository=self.repository)

    async def execute(self, borrow_id: int, borrow_data: ReturnBorrowRequest):
        return await self.service.return_borrow(borrow_id, borrow_data)
