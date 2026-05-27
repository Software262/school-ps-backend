from app.core.db import SessionDep
from app.modules.inventory.application.get_items_inventory import GetItemsInventory
from app.modules.musical_band.schemas.request import FilterPaginationMusicalBand


class GetItemsMusicalBand:
    def __init__(self, session: SessionDep):
        self.app = GetItemsInventory(session=session)

    async def execute(self, filter_pagination: FilterPaginationMusicalBand):
        return await self.app.execute(filter_pagination=filter_pagination)
