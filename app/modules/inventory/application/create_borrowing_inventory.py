from app.modules.enrollment.domain.service import StudentService
from app.modules.enrollment.infrastructure.repository import SQLEnrollmentRepository
from app.modules.inventory.domain.service import InventoryService
from app.modules.inventory.infrastructure.repository import InventoryRepository
from app.modules.inventory.schemas.request import CreateBorrowRequest


class CreateItemBorrowing:
    def __init__(self, session):
        self.repository = InventoryRepository(session=session)
        self.service = InventoryService(
            repository=self.repository,
            studentService=StudentService(
                repository=SQLEnrollmentRepository(session=session)
            ),
        )

    async def execute(self, borrow_data: CreateBorrowRequest):
        return await self.service.create_borrow(borrow_data)
