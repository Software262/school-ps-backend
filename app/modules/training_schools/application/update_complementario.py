from app.core.db import SessionDep
from app.modules.training_schools.domain.entities import ComplementarioInfo
from app.modules.training_schools.domain.service import TrainingSchoolService
from app.modules.training_schools.infrastructure.enrollment_adapter import (
    EnrollmentAdapter,
)
from app.modules.training_schools.infrastructure.repository import (
    TrainingSchoolRepository,
)


class UpdateComplementario:
    def __init__(self, session: SessionDep) -> None:
        self.service = TrainingSchoolService(
            repository=TrainingSchoolRepository(session=session),
            enrollment=EnrollmentAdapter(session),
        )

    async def execute(
        self,
        complementario_id: int,
        nombre: str | None,
        anio: int | None,
        valor: int | None,
        estado_complemento: str | None,
        tipo_complementario_id: int | None,
    ) -> ComplementarioInfo:
        return await self.service.update_complementario(
            complementario_id=complementario_id,
            nombre=nombre,
            anio=anio,
            valor=valor,
            estado_complemento=estado_complemento,
            tipo_complementario_id=tipo_complementario_id,
        )
