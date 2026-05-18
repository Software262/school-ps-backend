from abc import ABC, abstractmethod
from typing import Sequence

from app.modules.inventory.infrastructure.models import (
    Inventario,
    Prestamo,
    TipoInventario,
)
from app.modules.inventory.schemas.request import (
    CreateBorrowRequest,
    CreateItemRequest,
    UpdateCompleteItemRequest,
    UpdateSingleItemRequest,
)


class InventoryRepository(ABC):
    @abstractmethod
    async def get_items_pagination(
        self, offset: int, limit: int
    ) -> Sequence[Inventario]:
        pass

    @abstractmethod
    async def get_type_id_by_name(self, item_type: str) -> int | None:
        pass

    @abstractmethod
    async def get_items_filter_pagination(
        self, offset: int, limit: int, type_id: int
    ) -> Sequence[Inventario]:
        pass

    @abstractmethod
    async def create_item(self, item_data: CreateItemRequest) -> Inventario:
        pass

    @abstractmethod
    async def create_type_inventory(self, name: str) -> TipoInventario:
        pass

    @abstractmethod
    async def get_item_by_id(self, item_id: int) -> Inventario | None:
        pass

    @abstractmethod
    async def update_item(
        self, item: Inventario, item_data: UpdateCompleteItemRequest
    ) -> Inventario:
        pass

    @abstractmethod
    async def create_borrow(self, borrow_data: CreateBorrowRequest) -> Prestamo:
        pass

    @abstractmethod
    async def update_amount_item(self, id: int, amount: int) -> Inventario:
        pass

    @abstractmethod
    async def edit_item(
        self, id: int, item_data: UpdateSingleItemRequest
    ) -> Inventario | None:
        pass
