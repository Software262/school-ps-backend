from app.core.db import SessionDep
from app.modules.inventory.application.update_item_inventory import UpdateItemInventory
from app.modules.sports.domain.service import SportsService


class UpdateItemDeportes(UpdateItemInventory):
    def __init__(self, session: SessionDep):
        super().__init__(session=session)
        self.service = SportsService(repository=self.repository)
