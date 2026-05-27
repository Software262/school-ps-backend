from fastapi import HTTPException, status

from app.modules.inventory.domain.service import InventoryService
from app.modules.inventory.infrastructure.repository import InventoryRepository
from app.modules.sports.schemas.request import CreateSportItemRequest

SPORT_TYPE_NAME = "deporte"


class CreateSportItem:
    def __init__(self, session):
        self.repository = InventoryRepository(session=session)
        self.service = InventoryService(repository=self.repository)

    async def execute(self, item_data: CreateSportItemRequest):
        sport_type_id = await self.repository.get_type_id_by_name(SPORT_TYPE_NAME)

        if not sport_type_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el tipo de inventario 'deporte'",
            )

        if item_data.tipo_inventario_id != sport_type_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El tipo de inventario no corresponde a deporte",
            )

        return await self.service.create_item(item_data)
