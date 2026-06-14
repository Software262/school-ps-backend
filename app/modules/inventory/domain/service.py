from typing import Sequence

from app.modules.inventory.application.contracts import InventoryEnrollmentService
from app.modules.inventory.domain.entities import (
    Borrowing,
    GetInventoryItem,
    StockState,
)
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
    UpdateSingleItemExtenseRequest,
    UpdateSingleItemRequest,
)
from app.shared.utils.filter_pagination import calculate_offset


class InventoryService:
    def __init__(
        self,
        repository: InventoryRepository,
        enrollment: InventoryEnrollmentService,
    ):
        self.repository = repository
        self.service = enrollment
        self.available_states = "disponible"
        self.borrowed_states = "prestado"
        self.maintenance_states = "mantenimiento"

    async def get_inventory(self, filter_pagination: FilterPaginationInventory):
        offset = calculate_offset(filter_pagination.page, filter_pagination.limit)

        type_id = None
        if filter_pagination.item_type:
            type_id = await self.repository.get_type_id_by_name(
                filter_pagination.item_type
            )
            if type_id is None:
                return 0, []

        count, inventarios = await self.repository.get_items_filter_pagination(
            offset=offset, limit=filter_pagination.limit, type_id=type_id
        )

        inv_ids = [inv.id for inv in inventarios if inv.id is not None]
        stock_rows = await self.repository.get_stocks_by_item_ids(inv_ids)

        stocks_by_item: dict[int, list[StockState]] = {}
        for stock, state in stock_rows:
            stocks_by_item.setdefault(stock.inventario_id, []).append(
                StockState(estado=state.nombre, cantidad=stock.cantidad)
            )

        return count, [
            GetInventoryItem(
                id=inv.id,
                tipo_inventario_id=inv.tipo_inventario_id,
                nombre=inv.nombre,
                cantidad_total=inv.cantidad_total,
                observacion=inv.observacion,
                stocks=stocks_by_item.get(inv.id, []),
            )
            for inv in inventarios
            if inv.id is not None
        ]

    async def get_statics(self, type_name: str):
        ids = await self.repository.get_all_inventory(type_name=type_name)

        inv_ids: list[int] = []
        amount_inventory: int = 0
        for id, amount in ids:
            if id is not None:
                inv_ids.append(id)
                amount_inventory += amount

        stock_rows = await self.repository.get_stocks_by_item_ids(list(inv_ids))

        count_available = 0
        count_borrowed = 0
        count_maintenance = 0
        for stock, state in stock_rows:
            if state.nombre == self.available_states:
                count_available += stock.cantidad

            if state.nombre == self.borrowed_states:
                count_borrowed += stock.cantidad

            if state.nombre == self.maintenance_states:
                count_maintenance += stock.cantidad

        return amount_inventory, count_available, count_borrowed, count_maintenance

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

        if not item.id:
            return None

        if self.service:
            student = self.service.get_student_by_id(
                student_id=borrow_data.estudiante_id
            )

            if not student:
                return None

            if not student.activo:
                return None

        available_state_id = await self.repository.get_state_id_by_name(
            self.available_states
        )

        if not available_state_id:
            return None

        inventory_available_stock = await self.repository.get_inventory_stock(
            state_id=available_state_id,
            item_id=item.id,
        )

        if not inventory_available_stock:
            return None

        if inventory_available_stock.cantidad < borrow_data.cantidad:
            return None

        borrow_state_id = await self.repository.get_state_id_by_name(
            self.borrowed_states
        )

        if not borrow_state_id:
            return None

        inventory_stock = await self.repository.get_inventory_stock(
            state_id=borrow_state_id,
            item_id=item.id,
        )

        if not inventory_stock:
            return None

        await self.repository.set_amount_stock_category(
            item_id=item.id,
            amount=(inventory_available_stock.cantidad - borrow_data.cantidad),
            category_name=self.available_states,
        )

        await self.repository.set_amount_stock_category(
            item_id=item.id,
            amount=(inventory_stock.cantidad + borrow_data.cantidad),
            category_name=self.borrowed_states,
        )

        borrow = await self.repository.create_borrow(
            borrow_data=borrow_data,
        )

        return borrow

    async def edit_item(self, item_id: int, item_data: UpdateSingleItemExtenseRequest):
        base_fields = ("tipo_inventario_id", "nombre", "cantidad_total", "observacion")
        set_fields = {
            k: v
            for k, v in item_data.model_dump(exclude_unset=True).items()
            if k in base_fields
        }

        data = UpdateSingleItemRequest(**set_fields)

        update = await self.repository.edit_item(id=item_id, item_data=data)

        if update and item_data.cantidad_disponible:
            await self.repository.set_amount_stock_category(
                item_id=item_id,
                amount=item_data.cantidad_disponible,
                category_name=self.available_states,
            )

        if update and item_data.cantidad_prestado:
            await self.repository.set_amount_stock_category(
                item_id=item_id,
                amount=item_data.cantidad_prestado,
                category_name=self.borrowed_states,
            )

        if update and item_data.cantidad_mantenimiento:
            await self.repository.set_amount_stock_category(
                item_id=item_id,
                amount=item_data.cantidad_mantenimiento,
                category_name=self.maintenance_states,
            )

        return update

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

        borrow = await self.repository.return_borrow(
            borrow_id=borrow_id, borrow_data=borrow_data
        )

        type_available_id = await self.repository.get_state_id_by_name(
            self.available_states
        )
        type_borrowed_id = await self.repository.get_state_id_by_name(
            self.borrowed_states
        )

        if not type_available_id or not type_borrowed_id:
            return None

        stock_available = await self.repository.get_inventory_stock(
            state_id=type_available_id, item_id=item.id
        )
        stock_borrowed = await self.repository.get_inventory_stock(
            state_id=type_borrowed_id, item_id=item.id
        )

        if not stock_available or not stock_borrowed:
            return None

        await self.repository.set_amount_stock_category(
            item_id=item.id,
            amount=(stock_available.cantidad + borrow_data.cantidad),
            category_name=self.available_states,
        )

        await self.repository.set_amount_stock_category(
            item_id=item.id,
            amount=(stock_borrowed.cantidad - borrow_data.cantidad),
            category_name=self.borrowed_states,
        )

        return borrow

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
