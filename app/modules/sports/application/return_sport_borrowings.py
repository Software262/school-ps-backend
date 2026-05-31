from app.modules.inventory.infrastructure.repository import InventoryRepository
from app.modules.inventory.schemas.request import ReturnBorrowRequest
from app.modules.sports.domain.service import SportsService


class ReturnSportBorrowing:
    def __init__(self, session):
        self.repository = InventoryRepository(session=session)
        self.service = SportsService(repository=self.repository)

    async def execute(self, borrow_id: int, borrow_data: ReturnBorrowRequest):
        return await self.service.return_sport_borrow(borrow_id, borrow_data)
