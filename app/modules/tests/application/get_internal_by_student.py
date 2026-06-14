from app.modules.tests.domain.service import InternalTestService
from app.modules.tests.infrastructure.enrollment_adapter import EnrollmentAdapter
from app.modules.tests.infrastructure.repository import InternalTestRepository
from app.shared.schemas.filter_pagination_request import FilterPagination


class GetInternalTestsByStudent:
    def __init__(self, session):
        self.service = InternalTestService(
            repository=InternalTestRepository(session=session),
            enrollment=EnrollmentAdapter(session),
        )

    async def execute(self, student_id: int, filter_pagination: FilterPagination):
        return await self.service.get_tests_by_student(
            student_id=student_id,
            filter_pagination=filter_pagination,
        )
