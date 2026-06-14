from app.core.db import SessionDep
from app.modules.inventory.application.return_borrowing import ReturnBorrowing
from app.modules.inventory.infrastructure.enrollment_adapter import (
    InventoryEnrollmentAdapter,
)
from app.modules.sports.domain.service import SportsService


class ReturnBorrowingDeportes(ReturnBorrowing):
    def __init__(self, session: SessionDep):
        super().__init__(session=session)
        _repo = self.service.repository
        self.service = SportsService(
            repository=_repo,
            enrollment=InventoryEnrollmentAdapter(session=session),
        )
