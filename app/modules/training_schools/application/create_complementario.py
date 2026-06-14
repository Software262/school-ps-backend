from app.core.db import SessionDep
from app.modules.training_schools.domain.entities import ComplementarioInfo
from app.modules.training_schools.domain.service import TrainingSchoolService
from app.modules.training_schools.infrastructure.enrollment_adapter import (
    EnrollmentAdapter,
)
from app.modules.training_schools.infrastructure.repository import (
    TrainingSchoolRepository,
)


class CreateComplementario:
    def __init__(self, session: SessionDep) -> None:
        self.service = TrainingSchoolService(
            repository=TrainingSchoolRepository(session=session),
            enrollment=EnrollmentAdapter(session),
        )

    async def execute(
        self,
        nombre: str,
        anio: int,
        valor: int,
        estado_complemento: str,
        tipo_complementario_id: int,
    ) -> ComplementarioInfo:
        return await self.service.create_complementario(
            nombre=nombre,
            anio=anio,
            valor=valor,
            estado_complemento=estado_complemento,
            tipo_complementario_id=tipo_complementario_id,
        )
