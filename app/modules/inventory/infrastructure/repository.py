from datetime import datetime
from typing import Sequence

from sqlmodel import select

from app.core.db import SessionDep
from app.modules.inventory.domain.repositories import (
    InventoryRepository as InventoryRepositoryInterface,
)
from app.modules.inventory.infrastructure.models import (
    Inventario,
    Prestamo,
    TipoInventario,
    Novedad,
)
from app.modules.inventory.schemas.request import (
    CreateBorrowRequest,
    CreateItemRequest,
    InventoryItemRequest,
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
        ).one_or_none()

        return result.id if result else None

    async def get_items_filter_pagination(
        self, offset: int, limit: int, type_id: int | None
    ) -> Sequence[Inventario]:
        query = select(Inventario).offset(offset).limit(limit)

        if type_id is not None:
            query = query.where(Inventario.tipo_inventario_id == type_id)

        return self.session.exec(query).all()

    async def create_item(self, item_data: CreateItemRequest):
        new_item = Inventario(
            tipo_inventario_id=item_data.tipo_inventario_id,
            nombre=item_data.nombre,
            cantidad=item_data.cantidad,
            estado_objeto=item_data.estado_objeto,
            observacion=item_data.observacion,
        )

        self.session.add(new_item)
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

    async def update_item(self, item: Inventario, item_data: UpdateCompleteItemRequest):
        item.tipo_inventario_id = item_data.tipo_inventario_id
        item.nombre = item_data.nombre
        item.cantidad = item_data.cantidad
        item.estado_objeto = item_data.estado_objeto
        item.observacion = item_data.observacion

        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)

        return item

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

    async def get_borrowing(self, borrow_id: int) -> Prestamo | None:
        borrow = self.session.exec(
            select(Prestamo).where(Prestamo.id == borrow_id)
        ).first()

        return borrow

    async def return_borrow(self, borrow_id: int, borrow_data: ReturnBorrowRequest):
        borrow = self.session.exec(
            select(Prestamo).where(
                Prestamo.id == borrow_id
                and Prestamo.inventario_id == borrow_data.inventario_id
                and Prestamo.estudiante_id == borrow_data.estudiante_id
            )
        ).one()
        borrow.fecha_devolucion = datetime.now()
        borrow.estado_prestamo = False
        borrow.cantidad = borrow_data.cantidad
        borrow.observacion = borrow_data.observacion
        self.session.add(borrow)
        self.session.commit()
        self.session.refresh(borrow)

        return borrow

    async def get_borrowings_pagination(
        self, offset: int, limit: int, active: bool | None, type_id: int | None
    ) -> Sequence[Prestamo]:
        query = select(Prestamo).offset(offset).limit(limit)

        if active is not None:
            query = query.where(Prestamo.estado_prestamo == active)

        if type_id is not None:
            query = query.join(Inventario).where(
                Inventario.tipo_inventario_id == type_id
            )

        return self.session.exec(query).all()

    async def create_items_batch(self, create_items_data: list[InventoryItemRequest]):
        inventory: list[Inventario] = []
        for _, data in enumerate(create_items_data):
            item: Inventario = Inventario(
                tipo_inventario_id=data.tipo_inventario_id,
                cantidad=data.cantidad,
                nombre=data.nombre,
                estado_objeto=data.estado_objeto,
                observacion=data.observacion,
            )

            self.session.add(item)
            self.session.commit()
            self.session.refresh(item)

            inventory.append(item)

        return inventory

    async def create_novedad(self, prestamo_id: int, descripcion: str) -> Novedad:
        nueva_novedad = Novedad(
            prestamo_id=prestamo_id, descripcion=descripcion, resuelta=False
        )
        self.session.add(nueva_novedad)
        self.session.commit()
        self.session.refresh(nueva_novedad)
        return nueva_novedad

    async def finalize_chess_return(self, borrow: Prestamo, item: Inventario) -> None:
        self.session.add(borrow)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(borrow)
        self.session.refresh(item)
