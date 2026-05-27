from fastapi import HTTPException, status

from app.modules.inventory.domain.service import InventoryService
from app.modules.inventory.infrastructure.repository import InventoryRepository
from app.modules.inventory.schemas.request import CreateBorrowRequest

SPORT_TYPE_NAME = "deporte"


class CreateSportBorrowing:
    def __init__(self, session):
        self.repository = InventoryRepository(session=session)
        self.service = InventoryService(repository=self.repository)

    async def execute(self, borrow_data: CreateBorrowRequest):
        sport_type_id = await self.repository.get_type_id_by_name(SPORT_TYPE_NAME)

        if not sport_type_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el tipo de inventario 'deporte'",
            )

        # Validar que el item del préstamo pertenece a deportes
        item = await self.repository.get_item_by_id(borrow_data.inventario_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item no encontrado",
            )
        if item.tipo_inventario_id != sport_type_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El item no pertenece al inventario de deporte",
            )

        return await self.service.create_borrow(borrow_data)
