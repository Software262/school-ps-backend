from app.core.db import SessionDep
from app.modules.inventory.application.create_item_inventory import CreateItemInventory
from app.modules.sports.domain.service import DeportesService
from app.modules.sports.schemas.request import CreateSportItemRequest


class CreateItemDeportes(CreateItemInventory):
    def __init__(self, session: SessionDep):
        super().__init__(session=session)
        self._service = DeportesService(repository=self.repository)

    async def _execute(self, item_data: CreateSportItemRequest):
        return await self._service.create_item(item_data=item_data)
