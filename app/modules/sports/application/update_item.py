from app.core.db import SessionDep
from app.modules.inventory.application.edit_single_item import EditSingleItem
from app.modules.sports.domain.service import DeportesService
from app.modules.sports.schemas.request import UpdateItemDeportes


class UpdateItem(EditSingleItem):
    def __init__(self, session: SessionDep):
        super().__init__(session=session)
        self._service = DeportesService(repository=self.repository)

    async def _execute(self, item_id: int, item_data: UpdateItemDeportes):
        return await self._service.update_item(item_id=item_id, item_data=item_data)
