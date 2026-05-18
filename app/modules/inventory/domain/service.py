from app.modules.inventory.domain.repositories import InventoryRepository
from app.modules.inventory.schemas.request import (
    CreateBorrowRequest,
    CreateItemRequest,
    CreateTypeInventoryRequest,
    UpdateItemRequest,
)
from app.shared.schemas.filter_pagination import FilterPagination
from app.shared.utils.filter_pagination import calculate_offset


class InventoryService:
    def __init__(self, repository: InventoryRepository):
        self.repository = repository

    async def get_inventory(self, filter_pagination: FilterPagination):
        offset = calculate_offset(filter_pagination.page, filter_pagination.limit)

        if not filter_pagination.item_type:
            return await self.repository.get_items_pagination(
                offset=offset, limit=filter_pagination.limit
            )

        type_id = await self.repository.get_type_id_by_name(filter_pagination.item_type)
        if not type_id:
            return await self.repository.get_items_pagination(
                offset=offset, limit=filter_pagination.limit
            )

        return await self.repository.get_items_filter_pagination(
            offset=offset,
            limit=filter_pagination.limit,
            type_id=type_id,
        )

    async def create_item(self, item_data: CreateItemRequest):
        return await self.repository.create_item(item_data)

    async def create_type_inventory(self, type_data: CreateTypeInventoryRequest):
        return await self.repository.create_type_inventory(name=type_data.nombre)

    async def update_item(self, item_id: int, item_data: UpdateItemRequest):
        item = await self.repository.get_item_by_id(item_id)
        if not item:
            return None

        return await self.repository.update_item(item=item, item_data=item_data)

    async def create_borrow(self, borrow_data: CreateBorrowRequest):
        item = await self.repository.get_item_by_id(borrow_data.inventario_id)
        if not item:
            return None

        if borrow_data.cantidad > item.cantidad:
            return None

        item.cantidad -= borrow_data.cantidad

        if not item.id:
            return None

        borrow = await self.repository.create_borrow(borrow_data)

        if not borrow:
            return None

        await self.repository.update_amount_item(item.id, item.cantidad)

        return borrow
