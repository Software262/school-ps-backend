from app.core.db import SessionDep
from app.modules.inventory.application.get_borrowings import GetBorrowings


class GetBorrowingsMusicalBand(GetBorrowings):
    def __init__(self, session: SessionDep):
        super().__init__(session=session)
