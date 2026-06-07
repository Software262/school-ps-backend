from app.core.db import SessionDep
from app.modules.training_schools.domain.service import TrainingSchoolService
from app.modules.training_schools.infrastructure.enrollment_adapter import (
    EnrollmentAdapter,
)
from app.modules.training_schools.infrastructure.repository import (
    TrainingSchoolRepository,
)


class EnrollStudent:
    def __init__(self, session: SessionDep) -> None:
        self.service = TrainingSchoolService(
            repository=TrainingSchoolRepository(session=session),
            enrollment=EnrollmentAdapter(session),
        )

    async def execute(
        self,
        estudiante_id: int,
        complementario_id: int,
        periodo_id: int,
        mes: str,
        usuario_id: int,
        observaciones: str | None = None,
        valor_acordado: int | None = None,
        numero_comprobante: str | None = None,
    ):
        return await self.service.enroll_student(
            estudiante_id,
            complementario_id,
            periodo_id,
            mes,
            usuario_id,
            observaciones=observaciones,
            valor_acordado=valor_acordado,
            numero_comprobante=numero_comprobante,
        )
