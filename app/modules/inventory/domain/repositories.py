from sqlmodel import select

from app.core.db import SessionDep
from app.modules.inventory.infrastructure.models import Inventario


class InventoryRepository:
    def __init__(self, session: SessionDep):
        self.session = session

    async def get_inventory(self):
        # Implement logic to retrieve inventory data from the database
        return self.session.exec(select(Inventario)).all()
