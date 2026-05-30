from typing import Sequence

from app.modules.inventory.infrastructure.models import Inventario, Novedad, Prestamo
from app.modules.sports.domain.repositories import SportsRepository
from app.modules.sports.schemas.request import (
    CreateSportBorrowRequest,
    CreateSportItemRequest,
    CreateSportNovedadRequest,
    ResolveSportNovedadRequest,
    ReturnSportBorrowRequest,
    SportItemFileRequest,
    UpdateCompleteSportItemRequest,
    UpdateSportItemRequest,
)
from app.modules.sports.schemas.response import PazYSalvoStatusResponse
from app.shared.utils.filter_pagination import calculate_offset


class SportsService:
    def __init__(self, repository: SportsRepository):
        self.repository = repository

    # =========================================================
    # ITEMS
    # =========================================================

    async def get_sport_items(self, page: int, limit: int) -> Sequence[Inventario]:
        offset = calculate_offset(page, limit)
        return await self.repository.get_sport_items_paginated(offset=offset, limit=limit)

    async def create_sport_item(
        self, item_data: CreateSportItemRequest
    ) -> Inventario:
        tipo_id = await self.repository.ensure_sport_type_exists()
        return await self.repository.create_sport_item(
            item_data=item_data, tipo_inventario_id=tipo_id
        )

    async def update_sport_item_complete(
        self, item_id: int, item_data: UpdateCompleteSportItemRequest
    ) -> Inventario | None:
        """PUT — reemplaza el item completo. Valida que sea de tipo deporte."""
        item = await self.repository.get_sport_item_by_id(item_id)
        if not item:
            return None
        return await self.repository.update_sport_item_complete(
            item=item, item_data=item_data
        )

    async def update_sport_item_partial(
        self, item_id: int, item_data: UpdateSportItemRequest
    ) -> Inventario | None:
        """PATCH — actualiza solo los campos enviados. Valida que sea de tipo deporte."""
        item = await self.repository.get_sport_item_by_id(item_id)
        if not item:
            return None
        return await self.repository.update_sport_item_partial(
            item_id=item_id, item_data=item_data
        )

    async def create_sport_items_from_file(
        self, items_data: list[SportItemFileRequest]
    ) -> list[Inventario]:
        tipo_id = await self.repository.ensure_sport_type_exists()
        return await self.repository.create_sport_items_batch(
            items_data=items_data, tipo_inventario_id=tipo_id
        )

    # =========================================================
    # PRÉSTAMOS
    # =========================================================

    async def create_sport_borrow(
        self, borrow_data: CreateSportBorrowRequest
    ) -> Prestamo | None:
        """
        Reglas de negocio (BRD DEP-RF-01 / DEP-RF-02):
        - El item debe existir y ser de tipo deporte.
        - El estudiante no debe tener novedades abiertas en deportes.
        - Debe haber stock suficiente.
        """
        item = await self.repository.get_sport_item_by_id(borrow_data.inventario_id)
        if not item:
            return None  # item no encontrado o no es de tipo deporte

        # DEP-RF-01: verificar restricciones previas del estudiante
        open_novedades = await self.repository.get_open_novedades_by_student(
            borrow_data.estudiante_id
        )
        if open_novedades:
            return None  # estudiante tiene novedades deportivas sin resolver

        if borrow_data.cantidad > item.cantidad:
            return None  # stock insuficiente

        if not item.id:
            return None

        borrow = await self.repository.create_sport_borrow(borrow_data)
        if not borrow:
            return None

        item.cantidad -= borrow_data.cantidad
        await self.repository.update_sport_item_amount(item.id, item.cantidad)

        return borrow

    async def return_sport_borrow(
        self, borrow_id: int, borrow_data: ReturnSportBorrowRequest
    ) -> Prestamo | None:
        """
        Reglas de negocio (BRD DEP-RF-03):
        - El préstamo debe existir y pertenecer a un item de tipo deporte.
        - El préstamo debe estar activo.
        - Los datos de item, estudiante y cantidad deben coincidir.
        - La observación (estado en que regresa el implemento) es obligatoria.
        """
        item = await self.repository.get_sport_item_by_id(borrow_data.inventario_id)
        if not item or not item.id:
            return None

        borrow = await self.repository.get_sport_borrow_by_id(borrow_id)
        if not borrow:
            return None

        if borrow.inventario_id != borrow_data.inventario_id:
            return None
        if borrow.estudiante_id != borrow_data.estudiante_id:
            return None
        if borrow.cantidad != borrow_data.cantidad:
            return None
        if not borrow.estado_prestamo:
            return None  # préstamo ya fue devuelto

        item.cantidad += borrow_data.cantidad
        await self.repository.update_sport_item_amount(item.id, item.cantidad)

        return await self.repository.return_sport_borrow(
            borrow_id=borrow_id, borrow_data=borrow_data
        )

    async def get_sport_borrowings(
        self, page: int, limit: int, active: bool | None
    ) -> Sequence[Prestamo]:
        offset = calculate_offset(page, limit)
        return await self.repository.get_sport_borrowings_paginated(
            offset=offset, limit=limit, active=active
        )

    # =========================================================
    # NOVEDADES
    # =========================================================

    async def create_sport_novedad(
        self, novedad_data: CreateSportNovedadRequest
    ) -> Novedad | None:
        """
        Reglas de negocio (BRD DEP-RF-04):
        - El préstamo debe existir y ser de tipo deporte.
        - Solo se puede crear novedad sobre préstamos activos.
        """
        borrow = await self.repository.get_sport_borrow_by_id(novedad_data.prestamo_id)
        if not borrow:
            return None  # préstamo no encontrado o no es deportivo

        if not borrow.estado_prestamo:
            return None  # no se crea novedad sobre un préstamo ya cerrado

        return await self.repository.create_sport_novedad(
            prestamo_id=novedad_data.prestamo_id,
            descripcion=novedad_data.descripcion,
        )

    async def resolve_sport_novedad(
        self, novedad_id: int, resolve_data: ResolveSportNovedadRequest
    ) -> Novedad | None:
        """
        Reglas de negocio (BRD DEP-RF-05):
        - La novedad debe existir.
        - Solo se puede resolver si está abierta (resuelta=False).
        - Se requiere descripción de resolución.
        """
        novedad = await self.repository.get_novedad_by_id(novedad_id)
        if not novedad:
            return None

        if novedad.resuelta:
            return None  # ya fue resuelta anteriormente

        return await self.repository.resolve_sport_novedad(
            novedad_id=novedad_id, resolve_data=resolve_data
        )

    # =========================================================
    # PAZ Y SALVO
    # =========================================================

    async def get_paz_y_salvo_status(
        self, estudiante_id: int
    ) -> PazYSalvoStatusResponse:
        """
        Reglas de negocio (BRD DEP-RF-04 / RN-12 / RN-10):
        - Préstamos activos sin devolver → bloquea paz y salvo (ROJO).
        - Novedades abiertas sin resolver → bloquea paz y salvo (ROJO).
        - Sin pendientes → paz y salvo habilitado (VERDE).
        """
        active_borrows = await self.repository.get_active_borrows_by_student(
            estudiante_id
        )
        open_novedades = await self.repository.get_open_novedades_by_student(
            estudiante_id
        )

        tiene_prestamos_activos = len(active_borrows) > 0
        tiene_novedades_abiertas = len(open_novedades) > 0
        paz_y_salvo = not tiene_prestamos_activos and not tiene_novedades_abiertas

        if tiene_novedades_abiertas:
            detalle = (
                f"Estudiante tiene {len(open_novedades)} novedad(es) deportiva(s) "
                "sin resolver (daño, pérdida o pendiente de reposición)."
            )
        elif tiene_prestamos_activos:
            detalle = (
                f"Estudiante tiene {len(active_borrows)} implemento(s) deportivo(s) "
                "prestado(s) sin devolver."
            )
        else:
            detalle = "El estudiante está en paz y salvo en el módulo de Deportes."

        return PazYSalvoStatusResponse(
            estudiante_id=estudiante_id,
            tiene_prestamos_activos=tiene_prestamos_activos,
            tiene_novedades_abiertas=tiene_novedades_abiertas,
            paz_y_salvo=paz_y_salvo,
            detalle=detalle,
        )
