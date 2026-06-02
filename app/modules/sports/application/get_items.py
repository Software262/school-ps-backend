from app.core.db import SessionDep
from app.modules.inventory.application.get_items_inventory import GetItemsInventory


class GetItemsDeportes(GetItemsInventory):
    def __init__(self, session: SessionDep):
        super().__init__(session=session)
