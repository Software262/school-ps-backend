from abc import ABC, abstractmethod
from typing import Sequence

from app.modules.inventory.infrastructure.models import Inventario, Novedad, Prestamo
from app.modules.sports.schemas.request import (
    CreateSportBorrowRequest,
    CreateSportItemRequest,
    ResolveSportNovedadRequest,
    ReturnSportBorrowRequest,
    SportItemFileRequest,
    UpdateCompleteSportItemRequest,
    UpdateSportItemRequest,
)


class SportsRepository(ABC):

    # ---------- Tipo inventario ----------

    @abstractmethod
    async def get_sport_type_id(self) -> int | None:
        """Devuelve el ID del TipoInventario cuyo nombre es 'deporte'."""
        pass

    @abstractmethod
    async def ensure_sport_type_exists(self) -> int:
        """Crea el tipo 'deporte' si no existe y devuelve su ID."""
        pass

    # ---------- Items ----------

    @abstractmethod
    async def get_sport_items_paginated(
        self, offset: int, limit: int
    ) -> Sequence[Inventario]:
        pass

    @abstractmethod
    async def get_sport_item_by_id(self, item_id: int) -> Inventario | None:
        """Retorna el item solo si pertenece al tipo 'deporte'."""
        pass

    @abstractmethod
    async def create_sport_item(
        self, item_data: CreateSportItemRequest, tipo_inventario_id: int
    ) -> Inventario:
        pass

    @abstractmethod
    async def update_sport_item_complete(
        self, item: Inventario, item_data: UpdateCompleteSportItemRequest
    ) -> Inventario:
        pass

    @abstractmethod
    async def update_sport_item_partial(
        self, item_id: int, item_data: UpdateSportItemRequest
    ) -> Inventario | None:
        pass

    @abstractmethod
    async def update_sport_item_amount(self, item_id: int, amount: int) -> Inventario:
        pass

    @abstractmethod
    async def create_sport_items_batch(
        self, items_data: list[SportItemFileRequest], tipo_inventario_id: int
    ) -> list[Inventario]:
        pass

    # ---------- Préstamos ----------

    @abstractmethod
    async def create_sport_borrow(
        self, borrow_data: CreateSportBorrowRequest
    ) -> Prestamo:
        pass

    @abstractmethod
    async def get_sport_borrow_by_id(self, borrow_id: int) -> Prestamo | None:
        """Retorna el préstamo solo si su item pertenece al tipo 'deporte'."""
        pass

    @abstractmethod
    async def get_sport_borrowings_paginated(
        self, offset: int, limit: int, active: bool | None
    ) -> Sequence[Prestamo]:
        pass

    @abstractmethod
    async def return_sport_borrow(
        self, borrow_id: int, borrow_data: ReturnSportBorrowRequest
    ) -> Prestamo:
        pass

    # ---------- Novedades ----------

    @abstractmethod
    async def create_sport_novedad(
        self, prestamo_id: int, descripcion: str
    ) -> Novedad:
        pass

    @abstractmethod
    async def get_novedad_by_id(self, novedad_id: int) -> Novedad | None:
        pass

    @abstractmethod
    async def get_open_novedades_by_student(
        self, estudiante_id: int
    ) -> Sequence[Novedad]:
        """Novedades abiertas (resuelta=False) de préstamos deportivos del estudiante."""
        pass

    @abstractmethod
    async def resolve_sport_novedad(
        self, novedad_id: int, resolve_data: ResolveSportNovedadRequest
    ) -> Novedad:
        pass

    # ---------- Paz y salvo ----------

    @abstractmethod
    async def get_active_borrows_by_student(
        self, estudiante_id: int
    ) -> Sequence[Prestamo]:
        """Préstamos activos (estado_prestamo=True) de items deportivos del estudiante."""
        pass
