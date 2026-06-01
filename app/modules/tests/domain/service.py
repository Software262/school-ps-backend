from app.modules.tests.domain.repositories import InternalTestRepository
from app.modules.tests.schemas.request import (
    CreateTestDetailRequest,
    UpdateTestDetailRequest,
)
from app.shared.schemas.filter_pagination_request import FilterPagination
from app.shared.utils.filter_pagination import calculate_offset


class InternalTestService:
    def __init__(self, repository: InternalTestRepository):
        self.repository = repository

    async def get_all_tests(self, filter_pagination: FilterPagination):
        offset = calculate_offset(filter_pagination.page, filter_pagination.limit)

        return await self.repository.get_tests_pagination(
            offset=offset,
            limit=filter_pagination.limit,
        )

    async def get_test_by_id(self, test_id: int):
        return await self.repository.get_test_by_id(test_id)

    async def get_tests_by_student(
        self,
        student_id: int,
        filter_pagination: FilterPagination,
    ):
        offset = calculate_offset(filter_pagination.page, filter_pagination.limit)

        return await self.repository.get_tests_by_student(
            student_id=student_id,
            offset=offset,
            limit=filter_pagination.limit,
        )

    async def create_test(self, test_data: CreateTestDetailRequest):
        return await self.repository.create_test(test_data)

    async def update_test(self, test_id: int, test_data: UpdateTestDetailRequest):
        test = await self.repository.get_test_by_id(test_id)
        if not test:
            return None

        return await self.repository.update_test(test=test, test_data=test_data)
