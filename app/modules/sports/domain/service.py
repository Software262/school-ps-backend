from typing import Sequence

from app.modules.inventory.domain.repositories import InventoryRepository
from app.modules.sports.infrastructure.repository import SportsRepository
from app.modules.inventory.infrastructure.models import Inventario, Novedad, Prestamo
from app.modules.sports.schemas.request import (
    CreateSportBorrowRequest,
    CreateSportItemRequest,
    CreateSportNovedadRequest,
    ResolveSportNovedadRequest,
    ReturnSportBorrowRequest,
    UpdateCompleteSportItemRequest,
    UpdateSportItemRequest,
)
from app.modules.sports.schemas.response import PazYSalvoStatusResponse

TIPO_DEPORTE = "deporte"


class SportsService:
    def __init__(self, repository: InventoryRepository | SportsRepository):
        self.repository = repository

    # =========================================================
    # Helpers internos
    # =========================================================

    async def _get_sport_type_id(self) -> int | None:
        return await self.repository.get_type_id_by_name(TIPO_DEPORTE)

    async def _ensure_sport_type_exists(self) -> int:
        tipo_id = await self._get_sport_type_id()
        if tipo_id is None:
            tipo = await self.repository.create_type_inventory(TIPO_DEPORTE)
            return tipo.id or 0
        return tipo_id

    async def edit_item(
        self, item_id: int, item_data: UpdateSportItemRequest
    ) -> Inventario | None:
        item = await self._get_sport_item(item_id)
        if not item:
            return None
        item_data.tipo_inventario_id = None
        return await self.repository.edit_item(id=item_id, item_data=item_data)

    async def _get_sport_item(self, item_id: int) -> Inventario | None:
        """Devuelve el item solo si pertenece al tipo deporte."""
        item = await self.repository.get_item_by_id(item_id=item_id)
        if not item:
            return None
        tipo_id = await self._get_sport_type_id()
        if item.tipo_inventario_id != tipo_id:
            return None
        return item

    async def _get_sport_borrow(self, borrow_id: int) -> Prestamo | None:
        """Devuelve el préstamo solo si su item pertenece al tipo deporte."""
        borrow = await self.repository.get_borrowing(borrow_id=borrow_id)
        if not borrow:
            return None
        item = await self._get_sport_item(borrow.inventario_id)
        if not item:
            return None
        return borrow

    async def _get_open_novedades_by_student(
        self, estudiante_id: int
    ) -> Sequence[Novedad]:
        tipo_id = await self._get_sport_type_id()
        if tipo_id is None:
            return []
        # Filtramos desde los préstamos activos del estudiante en deportes

        # Buscamos novedades abiertas cuyo prestamo_id esté en ese conjunto
        # Usamos create_novedad no existe get — filtramos en memoria con lo disponible
        all_borrows = await self.repository.get_borrowings_pagination(
            offset=0, limit=1000, active=None, type_id=tipo_id
        )

        open_novedades = []
        for borrow in all_borrows:
            if borrow.estudiante_id != estudiante_id:
                continue
            for novedad in getattr(borrow, "novedades", []):
                if not novedad.resuelta:
                    open_novedades.append(novedad)
        return open_novedades

    # =========================================================
    # Items
    # =========================================================

    async def create_item(self, item_data: CreateSportItemRequest) -> Inventario:
        tipo_id = await self._ensure_sport_type_exists()
        item_data.tipo_inventario_id = tipo_id
        return await self.repository.create_item(item_data=item_data)

    async def update_item(
        self, item_id: int, item_data: UpdateCompleteSportItemRequest
    ) -> Inventario | None:
        item = await self._get_sport_item(item_id)
        if not item:
            return None
        item_data.tipo_inventario_id = item.tipo_inventario_id
        return await self.repository.edit_item(id=item_id, item_data=item_data)

    # =========================================================
    # Préstamos
    # =========================================================

    async def create_sport_borrow(
        self, borrow_data: CreateSportBorrowRequest
    ) -> Prestamo | None:
        item = await self._get_sport_item(borrow_data.inventario_id)
        if not item or not item.id:
            return None

        if borrow_data.cantidad > item.cantidad:
            return None

        open_novedades = await self._get_open_novedades_by_student(
            borrow_data.estudiante_id
        )
        if open_novedades:
            return None

        borrow = await self.repository.create_borrow(borrow_data=borrow_data)
        if not borrow:
            return None

        await self.repository.update_amount_item(
            id=item.id, amount=item.cantidad - borrow_data.cantidad
        )
        return borrow

    async def return_sport_borrow(
        self, borrow_id: int, borrow_data: ReturnSportBorrowRequest
    ) -> Prestamo | None:
        item = await self._get_sport_item(borrow_data.inventario_id)
        if not item or not item.id:
            return None

        borrow = await self._get_sport_borrow(borrow_id)
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

        await self.repository.update_amount_item(
            id=item.id, amount=item.cantidad + borrow_data.cantidad
        )
        return await self.repository.return_borrow(
            borrow_id=borrow_id, borrow_data=borrow_data
        )

    # =========================================================
    # Novedades
    # =========================================================

    async def create_sport_novedad(
        self, novedad_data: CreateSportNovedadRequest
    ) -> Novedad | None:
        borrow = await self._get_sport_borrow(novedad_data.prestamo_id)
        if not borrow:
            return None
        if not borrow.estado_prestamo:
            return None
        return await self.repository.create_novedad(
            prestamo_id=novedad_data.prestamo_id,
            descripcion=novedad_data.descripcion,
        )

    async def resolve_sport_novedad(
        self, novedad_id: int, resolve_data: ResolveSportNovedadRequest
    ) -> Novedad | None:
        assert isinstance(self.repository, SportsRepository)
        novedad = await self.repository.get_novedad_by_id(novedad_id)
        if not novedad or novedad.resuelta:
            return None
        novedad.resuelta = True
        novedad.descripcion = resolve_data.descripcion
        self.repository.session.add(novedad)
        self.repository.session.commit()
        self.repository.session.refresh(novedad)
        return novedad

    async def create_sport_items_from_file(self, items_data: list) -> list:
        tipo_id = await self._ensure_sport_type_exists()
        for item in items_data:
            item.tipo_inventario_id = tipo_id
        return await self.repository.create_items_batch(create_items_data=items_data)

    # =========================================================
    # Paz y salvo
    # =========================================================

    async def get_paz_y_salvo_status(
        self, estudiante_id: int
    ) -> PazYSalvoStatusResponse:
        tipo_id = await self._get_sport_type_id()

        active_borrows = []
        if tipo_id:
            all_borrows = await self.repository.get_borrowings_pagination(
                offset=0, limit=1000, active=True, type_id=tipo_id
            )
            active_borrows = [
                b for b in all_borrows if b.estudiante_id == estudiante_id
            ]

        open_novedades = await self._get_open_novedades_by_student(estudiante_id)

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
