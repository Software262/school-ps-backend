from datetime import datetime
from typing import Sequence

from sqlmodel import select

from app.core.db import SessionDep
from app.modules.inventory.infrastructure.models import (
    Inventario,
    Novedad,
    Prestamo,
    TipoInventario,
)
from app.modules.sports.domain.repositories import SportsRepository
from app.modules.sports.schemas.request import (
    CreateSportBorrowRequest,
    CreateSportItemRequest,
    ResolveSportNovedadRequest,
    ReturnSportBorrowRequest,
    SportItemFileRequest,
    UpdateCompleteSportItemRequest,
    UpdateSportItemRequest,
    TIPO_DEPORTE,
)


class SportsRepositoryImpl(SportsRepository):
    def __init__(self, session: SessionDep):
        self.session = session

    # =========================================================
    # Tipo inventario
    # =========================================================

    async def get_sport_type_id(self) -> int | None:
        result = self.session.exec(
            select(TipoInventario).where(TipoInventario.nombre == TIPO_DEPORTE)
        ).one_or_none()
        return result.id if result else None

    async def ensure_sport_type_exists(self) -> int:
        tipo = self.session.exec(
            select(TipoInventario).where(TipoInventario.nombre == TIPO_DEPORTE)
        ).one_or_none()

        if not tipo:
            tipo = TipoInventario(nombre=TIPO_DEPORTE)
            self.session.add(tipo)
            self.session.commit()
            self.session.refresh(tipo)

        return tipo.id  # type: ignore[return-value]

    # =========================================================
    # Items
    # =========================================================

    async def get_sport_items_paginated(
        self, offset: int, limit: int
    ) -> Sequence[Inventario]:
        tipo_id = await self.get_sport_type_id()
        if tipo_id is None:
            return []

        return self.session.exec(
            select(Inventario)
            .where(Inventario.tipo_inventario_id == tipo_id)
            .offset(offset)
            .limit(limit)
        ).all()

    async def get_sport_item_by_id(self, item_id: int) -> Inventario | None:
        """Devuelve el item solo si pertenece al tipo 'deporte'."""
        tipo_id = await self.get_sport_type_id()
        if tipo_id is None:
            return None

        return self.session.exec(
            select(Inventario).where(
                Inventario.id == item_id,
                Inventario.tipo_inventario_id == tipo_id,
            )
        ).one_or_none()

    async def create_sport_item(
        self, item_data: CreateSportItemRequest, tipo_inventario_id: int
    ) -> Inventario:
        new_item = Inventario(
            tipo_inventario_id=tipo_inventario_id,
            nombre=item_data.nombre,
            cantidad=item_data.cantidad,
            estado_objeto=item_data.estado_objeto,
            observacion=item_data.observacion,
        )
        self.session.add(new_item)
        self.session.commit()
        self.session.refresh(new_item)
        return new_item

    async def update_sport_item_complete(
        self, item: Inventario, item_data: UpdateCompleteSportItemRequest
    ) -> Inventario:
        item.nombre = item_data.nombre
        item.cantidad = item_data.cantidad
        item.estado_objeto = item_data.estado_objeto
        item.observacion = item_data.observacion
        # tipo_inventario_id NO se modifica: el item siempre permanece en 'deporte'
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    async def update_sport_item_partial(
        self, item_id: int, item_data: UpdateSportItemRequest
    ) -> Inventario | None:
        item = self.session.exec(
            select(Inventario).where(Inventario.id == item_id)
        ).one_or_none()
        if not item:
            return None

        update_data = item_data.model_dump(exclude_unset=True)
        # Nunca permitir cambiar el tipo de inventario desde este módulo
        update_data.pop("tipo_inventario_id", None)
        for field, value in update_data.items():
            setattr(item, field, value)

        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    async def update_sport_item_amount(self, item_id: int, amount: int) -> Inventario:
        item = self.session.exec(
            select(Inventario).where(Inventario.id == item_id)
        ).one()
        item.cantidad = amount
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    async def create_sport_items_batch(
        self, items_data: list[SportItemFileRequest], tipo_inventario_id: int
    ) -> list[Inventario]:
        inventory: list[Inventario] = []
        for data in items_data:
            item = Inventario(
                tipo_inventario_id=tipo_inventario_id,
                nombre=data.nombre,
                cantidad=data.cantidad,
                estado_objeto=data.estado_objeto,
                observacion=data.observacion,
            )
            self.session.add(item)
            self.session.commit()
            self.session.refresh(item)
            inventory.append(item)
        return inventory

    # =========================================================
    # Préstamos
    # =========================================================

    async def create_sport_borrow(
        self, borrow_data: CreateSportBorrowRequest
    ) -> Prestamo:
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

    async def get_sport_borrow_by_id(self, borrow_id: int) -> Prestamo | None:
        """Devuelve el préstamo solo si su item es de tipo 'deporte'."""
        tipo_id = await self.get_sport_type_id()
        if tipo_id is None:
            return None

        return self.session.exec(
            select(Prestamo)
            .join(Inventario)
            .where(
                Prestamo.id == borrow_id,
                Inventario.tipo_inventario_id == tipo_id,
            )
        ).one_or_none()

    async def get_sport_borrowings_paginated(
        self, offset: int, limit: int, active: bool | None
    ) -> Sequence[Prestamo]:
        tipo_id = await self.get_sport_type_id()
        if tipo_id is None:
            return []

        query = (
            select(Prestamo)
            .join(Inventario)
            .where(Inventario.tipo_inventario_id == tipo_id)
            .offset(offset)
            .limit(limit)
        )
        if active is not None:
            query = query.where(Prestamo.estado_prestamo == active)

        return self.session.exec(query).all()

    async def return_sport_borrow(
        self, borrow_id: int, borrow_data: ReturnSportBorrowRequest
    ) -> Prestamo:
        borrow = self.session.exec(
            select(Prestamo).where(Prestamo.id == borrow_id)
        ).one()
        borrow.fecha_devolucion = datetime.now()
        borrow.estado_prestamo = False
        borrow.observacion = borrow_data.observacion
        self.session.add(borrow)
        self.session.commit()
        self.session.refresh(borrow)
        return borrow

    # =========================================================
    # Novedades
    # =========================================================

    async def create_sport_novedad(
        self, prestamo_id: int, descripcion: str
    ) -> Novedad:
        novedad = Novedad(
            prestamo_id=prestamo_id,
            descripcion=descripcion,
            resuelta=False,
        )
        self.session.add(novedad)
        self.session.commit()
        self.session.refresh(novedad)
        return novedad

    async def get_novedad_by_id(self, novedad_id: int) -> Novedad | None:
        return self.session.exec(
            select(Novedad).where(Novedad.id == novedad_id)
        ).one_or_none()

    async def get_open_novedades_by_student(
        self, estudiante_id: int
    ) -> Sequence[Novedad]:
        tipo_id = await self.get_sport_type_id()
        if tipo_id is None:
            return []

        return self.session.exec(
            select(Novedad)
            .join(Prestamo)
            .join(Inventario)
            .where(
                Prestamo.estudiante_id == estudiante_id,
                Inventario.tipo_inventario_id == tipo_id,
                Novedad.resuelta == False,  # noqa: E712
            )
        ).all()

    async def resolve_sport_novedad(
        self, novedad_id: int, resolve_data: ResolveSportNovedadRequest
    ) -> Novedad:
        novedad = self.session.exec(
            select(Novedad).where(Novedad.id == novedad_id)
        ).one()
        novedad.resuelta = True
        novedad.descripcion = resolve_data.descripcion
        self.session.add(novedad)
        self.session.commit()
        self.session.refresh(novedad)
        return novedad

    # =========================================================
    # Paz y salvo
    # =========================================================

    async def get_active_borrows_by_student(
        self, estudiante_id: int
    ) -> Sequence[Prestamo]:
        tipo_id = await self.get_sport_type_id()
        if tipo_id is None:
            return []

        return self.session.exec(
            select(Prestamo)
            .join(Inventario)
            .where(
                Prestamo.estudiante_id == estudiante_id,
                Prestamo.estado_prestamo == True,  # noqa: E712
                Inventario.tipo_inventario_id == tipo_id,
            )
        ).all()
