from datetime import datetime
from typing import Sequence

from sqlmodel import col, func, or_, select

from app.core.db import SessionDep
from app.modules.inventory.domain.repositories import (
    InventoryRepository as InventoryRepositoryInterface,
)
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
    ReturnBorrowRequest,
    UpdateCompleteItemRequest,
    UpdateSingleItemRequest,
)


class InventoryRepository(InventoryRepositoryInterface):
    def __init__(self, session: SessionDep):
        self.session = session

    async def get_type_id_by_name(self, item_type: str) -> int | None:
        result = self.session.exec(
            select(TipoInventario).where(TipoInventario.nombre == item_type)
        ).first()

        if not result:
            return None

        return result.id

    async def get_items_filter_pagination(
        self, offset: int, limit: int, type_id: int | None, q: str | None
    ):
        inv_query = select(Inventario).offset(offset).limit(limit)
        count_query = select(func.count(col(Inventario.id)))

        if type_id is not None:
            inv_query = inv_query.where(Inventario.tipo_inventario_id == type_id)
            count_query = count_query.where(Inventario.tipo_inventario_id == type_id)

        if q is not None:
            inv_query = inv_query.where(
                or_(
                    col(Inventario.nombre).ilike(f"%{q.lower()}%"),
                    col(Inventario.observacion).ilike(f"%{q.lower()}%"),
                )
            )
            count_query = count_query.where(
                or_(
                    col(Inventario.nombre).ilike(f"%{q.lower()}%"),
                    col(Inventario.observacion).ilike(f"%{q.lower()}%"),
                )
            )

        return self.session.exec(count_query).one(), self.session.exec(inv_query).all()

    async def get_stocks_by_item_ids(self, item_ids: list[int]):
        if not item_ids:
            return []

        return self.session.exec(
            select(InventarioStock, EstadoInventario)
            .join(
                EstadoInventario,
                col(InventarioStock.estado_inventario_id) == col(EstadoInventario.id),
            )
            .where(col(InventarioStock.inventario_id).in_(item_ids))
        ).all()

    async def get_all_inventory(
        self, type_name: str
    ) -> Sequence[tuple[int | None, int]]:
        type_id = await self.get_type_id_by_name(item_type=type_name)

        if not type_id:
            return []

        return self.session.exec(
            select(col(Inventario.id), col(Inventario.cantidad_total)).where(
                col(Inventario.tipo_inventario_id) == type_id
            )
        ).all()

    async def create_item(self, item_data: CreateItemRequest):
        new_item = Inventario(
            tipo_inventario_id=item_data.tipo_inventario_id,
            nombre=item_data.nombre,
            cantidad_total=item_data.cantidad_total,
            observacion=item_data.observacion,
        )

        self.session.add(new_item)
        self.session.flush()

        available_state_id = await self.get_state_id_by_name("disponible")
        borrow_estado_id = await self.get_state_id_by_name("prestado")
        maintenance_state_id = await self.get_state_id_by_name("mantenimiento")

        if (
            not new_item.id
            or not available_state_id
            or not maintenance_state_id
            or not borrow_estado_id
        ):
            return None

        inventarioStocks: list[InventarioStock] = [
            InventarioStock(
                inventario_id=new_item.id,
                estado_inventario_id=available_state_id,
                cantidad=item_data.cantidad_total,
            ),
            InventarioStock(
                inventario_id=new_item.id,
                estado_inventario_id=maintenance_state_id,
                cantidad=0,
            ),
            InventarioStock(
                inventario_id=new_item.id,
                estado_inventario_id=borrow_estado_id,
                cantidad=0,
            ),
        ]

        self.session.add_all(inventarioStocks)
        self.session.commit()
        self.session.refresh(new_item)

        return new_item

    async def create_type_inventory(self, name: str):
        new_type = TipoInventario(nombre=name)

        self.session.add(new_type)
        self.session.commit()
        self.session.refresh(new_type)

        return new_type

    async def get_item_by_id(self, item_id: int):
        return self.session.get(Inventario, item_id)

    async def get_types_inventory_filter_pagination(self, offset: int, limit: int):
        query = select(TipoInventario).offset(offset).limit(limit)

        return self.session.exec(
            select(func.count(col(TipoInventario.id)))
        ).one(), self.session.exec(query).all()

    async def update_item(self, item: Inventario, item_data: UpdateCompleteItemRequest):
        item.tipo_inventario_id = item_data.tipo_inventario_id
        item.nombre = item_data.nombre
        item.cantidad_total = item_data.cantidad_total
        item.observacion = item_data.observacion

        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)

        return item

    async def get_state_by_id(self, state_id: int):
        return self.session.exec(
            select(EstadoInventario).where(col(EstadoInventario.id) == state_id)
        ).first()

    async def get_state_id_by_name(self, state_name: str):
        result = self.session.exec(
            select(col(EstadoInventario.id)).where(
                col(EstadoInventario.nombre) == state_name.lower()
            )
        ).first()

        return result

    async def get_inventory_stock(self, state_id: int, item_id: int):
        return self.session.exec(
            select(InventarioStock).where(
                col(InventarioStock.estado_inventario_id) == state_id,
                col(InventarioStock.inventario_id) == item_id,
            )
        ).first()

    async def create_borrow(self, borrow_data: CreateBorrowRequest):
        new_borrow = Prestamo(
            inventario_id=borrow_data.inventario_id,
            estudiante_id=borrow_data.estudiante_id,
            fecha_salida=borrow_data.fecha_salida,
            estado_prestamo=True,
            cantidad=borrow_data.cantidad,
            fecha_devolucion=None,
            observacion=borrow_data.observacion,
        )

        self.session.add(new_borrow)
        self.session.commit()
        self.session.refresh(new_borrow)

        return new_borrow

    async def update_amount_item(self, id: int, amount: int):
        item = self.session.exec(select(Inventario).where(Inventario.id == id)).one()

        item.cantidad = amount
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)

        return item

    async def edit_item(self, id: int, item_data: UpdateSingleItemRequest):
        item = self.session.exec(select(Inventario).where(Inventario.id == id)).one()
        update_data = item_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(item, field, value)

        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)

        return item

    async def set_amount_stock_category(
        self, item_id: int, amount: int, category_name: str
    ):
        type_id = await self.get_state_id_by_name(category_name)

        if not type_id:
            return None

        inventory_stock = self.session.exec(
            select(InventarioStock).where(
                InventarioStock.inventario_id == item_id,
                InventarioStock.estado_inventario_id == type_id,
            )
        ).one()

        if not inventory_stock:
            return None

        inventory_stock.cantidad = amount

        self.session.add(inventory_stock)
        self.session.commit()

        return None

    async def get_borrowing(self, borrow_id: int):
        borrow = self.session.exec(
            select(Prestamo).where(Prestamo.id == borrow_id)
        ).first()

        return borrow

    async def return_borrow(self, borrow_id: int, borrow_data: ReturnBorrowRequest):
        borrow = self.session.exec(
            select(Prestamo).where(
                Prestamo.id == borrow_id,
                Prestamo.inventario_id == borrow_data.inventario_id,
                Prestamo.estudiante_id == borrow_data.estudiante_id,
            )
        ).first()

        if borrow is None:
            raise ValueError("Prestamo no encontrado")

        borrow.fecha_devolucion = datetime.now()
        borrow.estado_prestamo = False
        borrow.cantidad = borrow_data.cantidad
        borrow.observacion = borrow_data.observacion

        self.session.add(borrow)
        self.session.commit()
        self.session.refresh(borrow)

        return borrow

    async def get_borrowings_pagination(
        self,
        offset: int,
        limit: int,
        active: bool | None,
        type_id: int | None,
        q: str | None,
    ):
        query = select(Prestamo).join(Inventario)
        query_count = select(func.count(col(Prestamo.id))).join(Inventario)

        if active is not None:
            query = query.where(Prestamo.estado_prestamo == active)
            query_count = query_count.where(Prestamo.estado_prestamo == active)

        if type_id is not None:
            query = query.where(Inventario.tipo_inventario_id == type_id)
            query_count = query_count.where(Inventario.tipo_inventario_id == type_id)

        if q is not None:
            query = query.where(col(Inventario.nombre).ilike(f"%{q.lower()}%"))
            query_count = query_count.where(
                col(Inventario.nombre).ilike(f"%{q.lower()}%")
            )

        return self.session.exec(query_count).one(), self.session.exec(
            query.offset(offset).limit(limit)
        ).all()

    def rollback(self) -> None:
        self.session.rollback()

    def _set_stock(
        self,
        item_id: int,
        state_id: int,
        amount: int,
        stock: InventarioStock | None,
    ) -> None:
        if stock is not None:
            stock.cantidad = amount
            self.session.add(stock)
        else:
            self.session.add(
                InventarioStock(
                    inventario_id=item_id,
                    estado_inventario_id=state_id,
                    cantidad=amount,
                )
            )

    async def get_item_by_name(self, nombre: str) -> Inventario | None:
        return self.session.exec(
            select(Inventario).where(func.lower(Inventario.nombre) == nombre.lower())
        ).first()

    async def get_stocks_map_by_item_id(
        self, item_id: int
    ) -> dict[int, InventarioStock]:
        return {
            stock.estado_inventario_id: stock
            for stock in self.session.exec(
                select(InventarioStock).where(InventarioStock.inventario_id == item_id)
            ).all()
        }

    async def create_imported_item(
        self,
        tipo_id: int,
        nombre: str,
        cantidad_total: int,
        observacion: str | None,
        stocks: dict[int, int],
    ) -> Inventario:
        new_item = Inventario(
            tipo_inventario_id=tipo_id,
            nombre=nombre,
            cantidad_total=cantidad_total,
            observacion=observacion,
        )
        self.session.add(new_item)
        self.session.flush()

        if new_item.id is None:
            raise ValueError("No se pudo crear el articulo")

        self.session.add_all(
            [
                InventarioStock(
                    inventario_id=new_item.id,
                    estado_inventario_id=state_id,
                    cantidad=cantidad,
                )
                for state_id, cantidad in stocks.items()
            ]
        )
        self.session.commit()
        return new_item

    async def update_imported_item(
        self,
        item: Inventario,
        tipo_id: int,
        cantidad_total: int,
        observacion: str | None,
        stocks: dict[int, int],
        existing_stocks: dict[int, InventarioStock],
    ) -> Inventario:
        if item.id is None:
            raise ValueError("El articulo no tiene identificador")

        item.tipo_inventario_id = tipo_id
        item.cantidad_total = cantidad_total
        item.observacion = observacion
        self.session.add(item)

        for state_id, cantidad in stocks.items():
            self._set_stock(item.id, state_id, cantidad, existing_stocks.get(state_id))

        self.session.commit()
        return item

    async def create_novedad(self, prestamo_id: int, descripcion: str):
        nueva_novedad = Novedad(
            prestamo_id=prestamo_id, descripcion=descripcion, resuelta=False
        )
        self.session.add(nueva_novedad)
        self.session.commit()
        self.session.refresh(nueva_novedad)
        return nueva_novedad

    async def finalize_chess_return(self, borrow: Prestamo, item: Inventario):
        self.session.add(borrow)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(borrow)
        self.session.refresh(item)

    async def get_novedad_by_borrow_id(self, prestamo_id: int):
        return self.session.exec(
            select(Novedad).where(Novedad.prestamo_id == prestamo_id)
        ).first()

    async def update_item_estado(self, item_id: int, estado: str):
        item = self.session.exec(
            select(Inventario).where(Inventario.id == item_id)
        ).one()

        item.estado_objeto = estado
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)

        return item

    async def update_borrow_observacion(self, prestamo_id: int, observacion: str):
        prestamo = self.session.exec(
            select(Prestamo).where(Prestamo.id == prestamo_id)
        ).one()
        prestamo.observacion = observacion
        self.session.add(prestamo)
        self.session.commit()
        self.session.refresh(prestamo)
        return prestamo

    async def get_type_by_name(self, name: str):
        return self.session.exec(
            select(TipoInventario).where(col(TipoInventario.nombre) == name)
        ).first()
