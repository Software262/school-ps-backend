from app.core.db import SessionDep
from app.modules.peace_safe.domain.service import PeaceSafeService
from app.modules.peace_safe.infrastructure.repository import PeaceSafeRepository
from app.modules.peace_safe.schemas.response import GenerateResponse


class GenerateStudentPazYSalvo:
    def __init__(self, session: SessionDep):
        self.service = PeaceSafeService(PeaceSafeRepository(session))

    async def execute(
        self, estudiante_id: int, usuario_id: int
    ) -> GenerateResponse | None:
        return self.service.generate_student_pazysalvo(estudiante_id, usuario_id)


class GenerateTeacherPazYSalvo:
    def __init__(self, session: SessionDep):
        self.service = PeaceSafeService(PeaceSafeRepository(session))

    async def execute(
        self, docente_id: int, usuario_id: int
    ) -> GenerateResponse | None:
        return self.service.generate_teacher_pazysalvo(docente_id, usuario_id)


class GetPazYSalvoDetail:
    def __init__(self, session: SessionDep):
        self.service = PeaceSafeService(PeaceSafeRepository(session))

    async def execute(self, pazysalvo_id: int) -> dict | None:
        return self.service.get_detail_status(pazysalvo_id)
