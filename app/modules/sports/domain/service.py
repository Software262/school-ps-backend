from app.modules.inventory.domain.repositories import InventoryRepository
from app.modules.sports.schemas.request import (
    CreateSportItemRequest,
    UpdateItemDeportes,
)


class DeportesService:
    def __init__(self, repository: InventoryRepository):
        self.repository = repository

    async def validate_deportes(self, item_id: int):
        type_id = await self.repository.get_type_id_by_name("deporte")

        if not type_id:
            return False

        if item_id != type_id:
            return False

        return True

    async def create_item(self, item_data: CreateSportItemRequest):
        valid = await self.validate_deportes(item_id=item_data.tipo_inventario_id)

        if not valid:
            return None

        return await self.repository.create_item(item_data=item_data)

    async def update_item(self, item_id: int, item_data: UpdateItemDeportes):
        item = await self.repository.get_item_by_id(item_id=item_id)

        if not item:
            return None

        valid = await self.validate_deportes(item_id=item.tipo_inventario_id)

        if not valid:
            return None

        item_data.tipo_inventario_id = item.tipo_inventario_id

        return await self.repository.edit_item(id=item_id, item_data=item_data)
