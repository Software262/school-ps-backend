from app.modules.tests.domain.service import InternalTestService
from app.modules.tests.infrastructure.repository import InternalTestRepository
from app.shared.schemas.filter_pagination_request import FilterPagination


class GetInternalTests:
    def __init__(self, session):
        self.repository = InternalTestRepository(session=session)
        self.service = InternalTestService(repository=self.repository)

    async def execute(self, filter_pagination: FilterPagination):
        return await self.service.get_all_tests(filter_pagination=filter_pagination)
