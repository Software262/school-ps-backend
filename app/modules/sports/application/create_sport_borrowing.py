from app.modules.inventory.infrastructure.repository import InventoryRepository
from app.modules.inventory.schemas.request import CreateBorrowRequest
from app.modules.sports.domain.service import SportsService


class CreateSportBorrowing:
    def __init__(self, session):
        self.repository = InventoryRepository(session=session)
        self.service = SportsService(repository=self.repository)

    async def execute(self, borrow_data: CreateBorrowRequest):
        return await self.service.create_sport_borrow(borrow_data)
