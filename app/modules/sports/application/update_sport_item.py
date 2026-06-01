from app.core.db import SessionDep
from app.modules.inventory.application.edit_single_item import EditSingleItem
from app.modules.sports.domain.service import SportsService
from app.modules.sports.schemas.request import UpdateCompleteSportItemRequest


class UpdateSportItem(EditSingleItem):
    def __init__(self, session: SessionDep):
        super().__init__(session=session)
        self._service = SportsService(repository=self.repository)

    async def _execute(self, item_id: int, item_data: UpdateCompleteSportItemRequest):
        return await self._service.update_item(item_id=item_id, item_data=item_data)