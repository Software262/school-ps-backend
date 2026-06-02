from app.modules.inventory.domain.repositories import InventoryRepository
from app.modules.inventory.domain.service import InventoryService


from app.modules.inventory.schemas.request import (
    CreateItemRequest,
    ReturnBorrowRequest,
    UpdateCompleteItemRequest,
    UpdateSingleItemRequest,
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

    async def edit_item(self, item_id: int, item_data: UpdateSingleItemRequest):
        if item_data.tipo_inventario_id is not None:
            await self.validate_sport_type(item_data.tipo_inventario_id)
        return await super().edit_item(item_id=item_id, item_data=item_data)

    async def return_borrow(self, borrow_id: int, borrow_data: ReturnBorrowRequest):
        await self.validate_sport_type(borrow_data.inventario_id)
        return await super().return_borrow(borrow_id=borrow_id, borrow_data=borrow_data)
