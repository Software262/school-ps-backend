from app.core.db import SessionDep
from app.modules.inventory.application.edit_single_item import EditSingleItem
from app.modules.sports.domain.service import SportsService


class EditItemDeportes(EditSingleItem):
    def __init__(self, session: SessionDep):
        super().__init__(session=session)
        self.service = SportsService(repository=self.repository)
