from fastapi import HTTPException, status

from app.modules.inventory.domain.service import InventoryService
from app.modules.inventory.infrastructure.repository import InventoryRepository
from app.modules.inventory.schemas.request import ReturnBorrowRequest

SPORT_TYPE_NAME = "deporte"


class ReturnSportBorrowing:
    def __init__(self, session):
        self.repository = InventoryRepository(session=session)
        self.service = InventoryService(repository=self.repository)

    async def execute(self, borrow_id: int, borrow_data: ReturnBorrowRequest):
        sport_type_id = await self.repository.get_type_id_by_name(SPORT_TYPE_NAME)

        if not sport_type_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el tipo de inventario 'deporte'",
            )

        # Validar que el préstamo corresponde a un item de deporte
        borrowing = await self.repository.get_borrowing(borrow_id)
        if not borrowing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Préstamo no encontrado",
            )

        item = await self.repository.get_item_by_id(borrowing.inventario_id)
        if not item or item.tipo_inventario_id != sport_type_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El préstamo no corresponde a un item de deporte",
            )

        return await self.service.return_borrow(borrow_id, borrow_data)
