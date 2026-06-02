from app.modules.inventory.domain.repositories import InventoryRepository
from app.modules.inventory.domain.service import InventoryService
from app.modules.inventory.schemas.request import UpdateCompleteItemRequest

from app.modules.sports.schemas.request import (
    CreateItemRequest,
)


class InvalidSportItem(Exception):
    pass


class SportTypeNotFound(Exception):
    pass


class SportItemNotFound(Exception):
    pass


class SportsService(InventoryService):
    def __init__(self, repository: InventoryRepository):
        super().__init__(repository=repository)

    async def validate_sport_type(self, tipo_inventario_id: int):

        sport_type = await self.repository.get_type_id_by_name("deporte")

        if not sport_type:
            raise SportTypeNotFound("Sport type does not exist")

        if int(sport_type) != int(tipo_inventario_id):
            raise InvalidSportItem("Item does not belong to sports")

        return sport_type

    async def create_item(self, item_data: CreateItemRequest):

        await self.validate_sport_type(item_data.tipo_inventario_id)

        return await self.repository.create_item(item_data=item_data)

    async def update_item(self, item_id: int, item_data: UpdateCompleteItemRequest):
        await self.validate_sport_type(item_data.tipo_inventario_id)
        return await super().update_item(item_id=item_id, item_data=item_data)
