from abc import ABC, abstractmethod
from typing import Sequence

from app.modules.inventory.infrastructure.models import (
    EstadoInventario,
    Inventario,
    InventarioStock,
    Novedad,
    Prestamo,
    TipoInventario,
)
from app.modules.inventory.schemas.request import (
    CreateBorrowRequest,
    CreateItemRequest,
    InventoryItemRequest,
    ReturnBorrowRequest,
    UpdateCompleteItemRequest,
    UpdateSingleItemRequest,
)


class InventoryRepository(ABC):
    @abstractmethod
    async def get_type_id_by_name(self, item_type: str) -> int | None:
        pass

    @abstractmethod
    async def get_items_filter_pagination(
        self, offset: int, limit: int, type_id: int | None, q: str | None
    ) -> tuple[int, Sequence[Inventario]]:
        pass

    @abstractmethod
    async def get_stocks_by_item_ids(
        self, item_ids: list[int]
    ) -> Sequence[tuple[InventarioStock, EstadoInventario]]:
        pass

    @abstractmethod
    async def get_all_inventory(
        self, type_name: str
    ) -> Sequence[tuple[int | None, int]]:
        pass

    @abstractmethod
    async def create_item(self, item_data: CreateItemRequest) -> Inventario | None:
        pass

    @abstractmethod
    async def create_type_inventory(self, name: str) -> TipoInventario:
        pass

    @abstractmethod
    async def get_types_inventory_filter_pagination(
        self, offset: int, limit: int
    ) -> tuple[int, Sequence[TipoInventario]]:
        pass

    @abstractmethod
    async def get_type_by_name(self, name: str) -> TipoInventario | None:
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
    async def get_state_by_id(self, state_id: int) -> EstadoInventario | None:
        pass

    @abstractmethod
    async def get_state_id_by_name(self, state_name: str) -> int | None:
        pass

    @abstractmethod
    async def get_inventory_stock(
        self, state_id: int, item_id: int
    ) -> InventarioStock | None:
        pass

    @abstractmethod
    async def set_amount_stock_category(
        self, item_id: int, amount: int, category_name: str
    ) -> None:
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

    @abstractmethod
    async def get_borrowing(self, borrow_id: int) -> Prestamo | None:
        pass

    @abstractmethod
    async def return_borrow(
        self, borrow_id: int, borrow_data: ReturnBorrowRequest
    ) -> Prestamo:
        pass

    @abstractmethod
    async def get_borrowings_pagination(
        self,
        offset: int,
        limit: int,
        active: bool | None,
        type_id: int | None,
        q: str | None,
    ) -> tuple[int, Sequence[Prestamo]]:
        pass

    @abstractmethod
    async def create_items_batch(
        self, create_items_data: list[InventoryItemRequest]
    ) -> list[Inventario]:
        pass

    @abstractmethod
    async def create_novedad(self, prestamo_id: int, descripcion: str) -> Novedad:
        pass

    @abstractmethod
    async def finalize_chess_return(self, borrow: Prestamo, item: Inventario) -> None:
        pass

    @abstractmethod
    async def get_novedad_by_borrow_id(self, prestamo_id: int) -> Novedad | None:
        pass

    @abstractmethod
    async def update_item_estado(self, item_id: int, estado: str) -> Inventario:
        pass
