from sqlmodel import select

from app.core.db import SessionDep
from app.modules.inventory.infrastructure.models import (
    Inventario,
    Prestamo,
    TipoInventario,
)
from app.modules.inventory.schemas.request import (
    CreateBorrowRequest,
    CreateItemRequest,
    UpdateItemRequest,
)


class InventoryRepository:
    def __init__(self, session: SessionDep):
        self.session = session

    async def get_items_pagination(self, offset: int, limit: int):
        return self.session.exec(select(Inventario).offset(offset).limit(limit)).all()

    async def get_type_id_by_name(self, item_type: str) -> int | None:
        result = self.session.exec(
            select(TipoInventario).where(TipoInventario.nombre == item_type)
        ).one_or_none()

        return result.id if result else None

    async def get_items_filter_pagination(self, offset: int, limit: int, type_id: int):
        return self.session.exec(
            select(Inventario)
            .where(Inventario.tipo_inventario_id == type_id)
            .offset(offset)
            .limit(limit)
        ).all()

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

    async def update_item(self, item: Inventario, item_data: UpdateItemRequest):
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
            estado_prestamo=borrow_data.estado_prestamo,
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
