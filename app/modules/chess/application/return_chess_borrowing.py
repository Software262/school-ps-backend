from app.modules.chess.domain.service import ChessService
from app.modules.inventory.infrastructure.repository import InventoryRepository
from app.modules.chess.schemas.request import ReturnChessRequest


class ReturnChessBorrowing:
    def __init__(self, session):
        self.repository = InventoryRepository(session=session)
        self.service = ChessService(repository=self.repository)

    async def execute(self, borrow_id: int, borrow_data: ReturnChessRequest):
        return await self.service.return_chess_borrow(borrow_id, borrow_data)
