from app.core.db import SessionDep
from app.modules.tests.infrastructure.repository import InternalTestRepository


class GetStudentTestStatus:
    def __init__(self, session: SessionDep):
        self.repository = InternalTestRepository(session)

    async def execute(self, student_id: int):
        tests = await self.repository.get_tests_by_student(
            student_id=student_id, offset=0, limit=1000
        )

        has_pending = False
        for t in tests:
            if t["estado"] in ["pendiente", "pago-parcial"]:
                has_pending = True
                break

        return {"has_debt": has_pending, "tests": tests}
