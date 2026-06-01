from sqlmodel import select

from app.core.db import SessionDep
from app.modules.inventory.infrastructure.repository import InventoryRepository
from app.modules.inventory.infrastructure.models import Novedad


class SportsRepository(InventoryRepository):
    def __init__(self, session: SessionDep):
        super().__init__(session=session)

    async def get_novedad_by_id(self, novedad_id: int) -> Novedad | None:
        return self.session.exec(
            select(Novedad).where(Novedad.id == novedad_id)
        ).one_or_none()
