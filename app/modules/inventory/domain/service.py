from typing import Sequence

from app.modules.enrollment.application.contracts import StudentQueryService
from app.modules.inventory.domain.entities import Borrowing
from app.modules.inventory.domain.repositories import InventoryRepository
from app.modules.inventory.infrastructure.models import Prestamo
from app.modules.inventory.schemas.request import (
    CreateBorrowRequest,
    CreateItemRequest,
    CreateTypeInventoryRequest,
    FilterPaginationInventory,
    FilterPaginationTypesInventory,
    InventoryItemRequest,
    ReturnBorrowRequest,
    UpdateCompleteItemRequest,
    UpdateSingleItemRequest,
)
from app.shared.utils.filter_pagination import calculate_offset


class InventoryService:
    def __init__(
        self,
        repository: InventoryRepository,
        studentService: StudentQueryService | None = None,
    ):
        self.repository = repository
        self.service = studentService

    async def get_inventory(self, filter_pagination: FilterPaginationInventory):
        offset = calculate_offset(filter_pagination.page, filter_pagination.limit)

        if not filter_pagination.item_type:
            return await self.repository.get_items_filter_pagination(
                offset=offset, limit=filter_pagination.limit, type_id=None
            )

        type_id = await self.repository.get_type_id_by_name(filter_pagination.item_type)

        if type_id is None:
            return 0, []

        return await self.repository.get_items_filter_pagination(
            offset=offset,
            limit=filter_pagination.limit,
            type_id=type_id,
        )

    async def get_types_inventory(
        self, filter_pagination: FilterPaginationTypesInventory
    ):
        offset = calculate_offset(filter_pagination.page, filter_pagination.limit)

        return await self.repository.get_types_inventory_filter_pagination(
            limit=filter_pagination.limit, offset=offset
        )

    async def create_item(self, item_data: CreateItemRequest):
        return await self.repository.create_item(item_data)

    async def create_type_inventory(self, type_data: CreateTypeInventoryRequest):
        name = type_data.nombre.strip().lower()

        return await self.repository.create_type_inventory(name=name)

    async def update_item(self, item_id: int, item_data: UpdateCompleteItemRequest):
        item = await self.repository.get_item_by_id(item_id)
        if not item:
            return None

        return await self.repository.update_item(item=item, item_data=item_data)

    async def get_type_by_name(self, name: str):
        return await self.repository.get_type_by_name(name=name)

    async def create_borrow(self, borrow_data: CreateBorrowRequest):
        item = await self.repository.get_item_by_id(borrow_data.inventario_id)
        if not item:
            return None

        if self.service:
            student = self.service.get_student_by_id(
                student_id=borrow_data.estudiante_id
            )

            if not student:
                return None

            if not student.activo:
                return None

        if borrow_data.cantidad > item.cantidad:
            return None

        if not item.id:
            return None

        borrow = await self.repository.create_borrow(borrow_data)

        if not borrow:
            return None

        item.cantidad -= borrow_data.cantidad

        await self.repository.update_amount_item(item.id, item.cantidad)

        return borrow

    async def edit_item(self, item_id: int, item_data: UpdateSingleItemRequest):
        return await self.repository.edit_item(id=item_id, item_data=item_data)

    async def return_borrow(self, borrow_id: int, borrow_data: ReturnBorrowRequest):
        item = await self.repository.get_item_by_id(borrow_data.inventario_id)
        if not item:
            return None

        if not item.id:
            return None

        borrow = await self.repository.get_borrowing(borrow_id)
        if not borrow:
            return None

        if not borrow.estado_prestamo:
            return None

        if borrow.inventario_id != borrow_data.inventario_id:
            return None

        if borrow.estudiante_id != borrow_data.estudiante_id:
            return None

        if borrow.cantidad != borrow_data.cantidad:
            return None

        item.cantidad += borrow_data.cantidad

        await self.repository.update_amount_item(item.id, item.cantidad)

        return await self.repository.return_borrow(
            borrow_id=borrow_id, borrow_data=borrow_data
        )

    async def format_borrowing(self, borrowings: Sequence[Prestamo]):
        result: list[Borrowing] = []

        for p in borrowings:
            if p.id is None or self.service is None:
                continue

            item = await self.repository.get_item_by_id(p.inventario_id)
            student = self.service.get_student_by_id(student_id=p.estudiante_id)

            if item is None or student is None:
                continue

            novedad = await self.repository.get_novedad_by_borrow_id(p.id)
            novedad_pendiente = novedad is not None and not novedad.resuelta

            result.append(
                Borrowing(
                    id=p.id,
                    nombre_articulo=item.nombre,
                    nombre_estudiante=student.nombre,
                    estudiante_id=p.estudiante_id,
                    inventario_id=p.inventario_id,
                    cantidad=p.cantidad,
                    estado_prestamo=p.estado_prestamo,
                    novedad_pendiente=novedad_pendiente,
                    fecha_devolucion=p.fecha_devolucion,
                    fecha_salida=p.fecha_salida,
                    observacion=p.observacion,
                )
            )

        return result

    async def get_borrowings(
        self, filter_pagination: FilterPaginationInventory, active: bool | None
    ):
        offset = calculate_offset(filter_pagination.page, filter_pagination.limit)

        if not filter_pagination.item_type:
            count, borrowings = await self.repository.get_borrowings_pagination(
                offset=offset,
                limit=filter_pagination.limit,
                active=active,
                type_id=None,
            )

            return count, (await self.format_borrowing(borrowings=borrowings))

        type_id = await self.repository.get_type_id_by_name(filter_pagination.item_type)

        if type_id is None:
            return 0, []

        count, borrowings = await self.repository.get_borrowings_pagination(
            offset=offset,
            limit=filter_pagination.limit,
            active=active,
            type_id=type_id,
        )

        return count, (await self.format_borrowing(borrowings=borrowings))

    async def create_items_inventory_from_file(
        self, create_items_data: list[InventoryItemRequest]
    ):
        return await self.repository.create_items_batch(
            create_items_data=create_items_data
        )
