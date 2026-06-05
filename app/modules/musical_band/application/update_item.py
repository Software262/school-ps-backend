from app.core.db import SessionDep
from app.modules.inventory.application.edit_single_item import EditSingleItem
from app.modules.musical_band.domain.service import MusicalBandService
from app.modules.musical_band.schemas.request import UpdateItemMusicalBand


class UpdateItem(EditSingleItem):
    def __init__(self, session: SessionDep):
        super().__init__(session=session)
        self._service = MusicalBandService(repository=self.repository)

    async def _execute(self, item_id: int, item_data: UpdateItemMusicalBand):
        return await self._service._update_item(item_id=item_id, item_data=item_data)
