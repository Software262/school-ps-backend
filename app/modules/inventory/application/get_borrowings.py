from typing import Sequence
from app.modules.inventory.infrastructure.models import Prestamo
from app.shared.schemas.filter_pagination import FilterPagination

from app.modules.inventory.infrastructure.repository import InventoryRepository

# AÑADIMOS EL IMPORT DEL SERVICIO
from app.modules.inventory.domain.service import InventoryService


class GetBorrowings:
    def __init__(self, session):
        # Instanciamos el repo y se lo inyectamos al servicio (cumpliendo la estructura)
        self.repository = InventoryRepository(session=session)
        self.service = InventoryService(self.repository)

    async def execute(
        self, filter_pagination: FilterPagination, active_only: bool = False
    ) -> Sequence[Prestamo]:
        # Delegamos la ejecución al servicio, tal como pidió Jefferson
        return await self.service.get_borrowings(
            filter_pagination=filter_pagination, active_only=active_only
        )
