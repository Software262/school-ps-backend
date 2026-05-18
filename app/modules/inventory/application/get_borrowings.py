from typing import Sequence
from app.modules.inventory.infrastructure.models import Prestamo
from app.shared.schemas.filter_pagination import FilterPagination

# Importamos el repositorio de infraestructura (como lo hace Jefferson en los otros archivos)
from app.modules.inventory.infrastructure.repository import InventoryRepositoryImpl

class GetBorrowings:
    def __init__(self, session):
        # Inyección de dependencias
        self.repository = InventoryRepositoryImpl(session)

    async def execute(self, filter_pagination: FilterPagination, active_only: bool = False) -> Sequence[Prestamo]:
        # Calculamos la paginación
        offset = (filter_pagination.page - 1) * filter_pagination.limit
        
        # Llamamos a la base de datos
        return await self.repository.get_borrowings_pagination(
            offset=offset, limit=filter_pagination.limit, active_only=active_only
        )