from app.core.db import SessionDep
from app.modules.inventory.application.create_borrowing_inventory import (
    CreateItemBorrowing,
)
from app.modules.sports.domain.service import SportsService


class CreateBorrowingDeportes(CreateItemBorrowing):
    def __init__(self, session: SessionDep):
        super().__init__(session=session)
        self.service = SportsService(repository=self.repository)
