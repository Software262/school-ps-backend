from typing import Sequence

from app.modules.inventory.domain.repositories import InventoryRepository
from app.modules.inventory.infrastructure.models import Inventario, Prestamo
from app.modules.inventory.schemas.request import (
    CreateBorrowRequest,
    ReturnBorrowRequest,
    UpdateCompleteItemRequest,
    UpdateSingleItemRequest,
)
from app.modules.sports.schemas.request import CreateSportItemRequest
from app.shared.schemas.filter_pagination import (
    FilterPagination,
    FilterPaginationBorrowings,
)
from app.shared.utils.filter_pagination import calculate_offset

SPORT_TYPE_NAME = "deporte"


class SportsService:
    def __init__(self, repository: InventoryRepository):
        self.repository = repository

    async def _get_sport_type_id(self) -> int | None:
        return await self.repository.get_type_id_by_name(SPORT_TYPE_NAME)

    async def _validate_item_is_sport(
        self, item: Inventario, sport_type_id: int
    ) -> bool:
        return item.tipo_inventario_id == sport_type_id

    # ── Items ──────────────────────────────────────────────────────────────────

    async def get_sport_items(
        self, filter_pagination: FilterPagination
    ) -> Sequence[Inventario]:
        sport_type_id = await self._get_sport_type_id()
        offset = calculate_offset(filter_pagination.page, filter_pagination.limit)
        return await self.repository.get_items_filter_pagination(
            offset=offset,
            limit=filter_pagination.limit,
            type_id=sport_type_id,
        )

    async def create_sport_item(
        self, item_data: CreateSportItemRequest
    ) -> Inventario | None:
        sport_type_id = await self._get_sport_type_id()
        if not sport_type_id or item_data.tipo_inventario_id != sport_type_id:
            return None
        return await self.repository.create_item(item_data)

    async def update_sport_item(
        self, item_id: int, item_data: UpdateCompleteItemRequest
    ) -> Inventario | None:
        sport_type_id = await self._get_sport_type_id()
        if not sport_type_id:
            return None

        item = await self.repository.get_item_by_id(item_id)
        if not item or not await self._validate_item_is_sport(item, sport_type_id):
            return None

        if item_data.tipo_inventario_id != sport_type_id:
            return None

        return await self.repository.update_item(item=item, item_data=item_data)

    async def edit_sport_item(
        self, item_id: int, item_data: UpdateSingleItemRequest
    ) -> Inventario | None:
        sport_type_id = await self._get_sport_type_id()
        if not sport_type_id:
            return None

        item = await self.repository.get_item_by_id(item_id)
        if not item or not await self._validate_item_is_sport(item, sport_type_id):
            return None

        if (
            item_data.tipo_inventario_id
            and item_data.tipo_inventario_id != sport_type_id
        ):
            return None

        return await self.repository.edit_item(id=item_id, item_data=item_data)

    # ── Préstamos ──────────────────────────────────────────────────────────────

    async def create_sport_borrow(
        self, borrow_data: CreateBorrowRequest
    ) -> Prestamo | None:
        sport_type_id = await self._get_sport_type_id()
        if not sport_type_id:
            return None

        item = await self.repository.get_item_by_id(borrow_data.inventario_id)
        if not item or not await self._validate_item_is_sport(item, sport_type_id):
            return None

        if borrow_data.cantidad > item.cantidad:
            return None

        borrow = await self.repository.create_borrow(borrow_data)
        if not borrow:
            return None

        if not item.id:
            return None

        item.cantidad -= borrow_data.cantidad
        await self.repository.update_amount_item(item.id, item.cantidad)

        return borrow

    async def get_sport_borrowings(
        self, filter_pagination: FilterPaginationBorrowings
    ) -> Sequence[Prestamo]:
        sport_type_id = await self._get_sport_type_id()
        offset = calculate_offset(filter_pagination.page, filter_pagination.limit)
        return await self.repository.get_borrowings_pagination(
            offset=offset,
            limit=filter_pagination.limit,
            active=filter_pagination.active,
            type_id=sport_type_id,
        )

    async def return_sport_borrow(
        self, borrow_id: int, borrow_data: ReturnBorrowRequest
    ) -> Prestamo | None:
        sport_type_id = await self._get_sport_type_id()
        if not sport_type_id:
            return None

        item = await self.repository.get_item_by_id(borrow_data.inventario_id)
        if not item or not await self._validate_item_is_sport(item, sport_type_id):
            return None

        borrow = await self.repository.get_borrowing(borrow_id)
        if not borrow:
            return None

        if borrow.inventario_id != borrow_data.inventario_id:
            return None
        if borrow.estudiante_id != borrow_data.estudiante_id:
            return None
        if borrow.cantidad != borrow_data.cantidad:
            return None
        if not borrow.estado_prestamo:
            return None
        if not item.id:
            return None

        item.cantidad += borrow_data.cantidad
        await self.repository.update_amount_item(item.id, item.cantidad)

        return await self.repository.return_borrow(
            borrow_id=borrow_id, borrow_data=borrow_data
        )
