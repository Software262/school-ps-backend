from app.modules.inventory.domain.repositories import InventoryRepository
from app.modules.inventory.domain.service import InventoryService
from app.modules.inventory.schemas.request import CreateBorrowRequest


class CreateItemBorrowing:
    def __init__(self, session):
        self.repository = InventoryRepository(session=session)
        self.service = InventoryService(repository=self.repository)

    async def execute(self, borrow_data: CreateBorrowRequest):
        return await self.service.create_borrow(borrow_data)
