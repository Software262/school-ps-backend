from app.core.db import SessionDep
from app.modules.tests.infrastructure.repository import InternalTestRepository


class DeleteInternalTest:
    def __init__(self, session: SessionDep):
        self.repository = InternalTestRepository(session)

    async def execute(self, test_id: int):
        test = await self.repository.get_test_by_id(test_id)
        if not test:
            raise ValueError("Test not found")

        self.repository.session.delete(test)
        self.repository.session.commit()
        return True
