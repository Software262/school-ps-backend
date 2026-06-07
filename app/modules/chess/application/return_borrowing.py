from app.core.db import SessionDep
from app.modules.chess.domain.service import ChessService
from app.modules.chess.infrastructure.repository import ChessRepository
from app.modules.inventory.infrastructure.repository import InventoryRepository
from app.modules.chess.schemas.request import ReturnChessBorrowRequest

class ReturnChessBorrowing:
    def __init__(self, session: SessionDep):
        self.chess_repo = ChessRepository(session=session)
        self.inventory_repo = InventoryRepository(session=session)
        self.service = ChessService(chess_repo=self.chess_repo, inventory_repo=self.inventory_repo)

    async def execute(self, prestamo_id: int, user_id: int, data: ReturnChessBorrowRequest):
        return await self.service.return_chess_borrow(prestamo_id, user_id, data)
