from app.core.db import SessionDep
from app.modules.training_schools.domain.entities import TipoComplementarioInfo
from app.modules.training_schools.domain.service import TrainingSchoolService
from app.modules.training_schools.infrastructure.enrollment_adapter import (
    EnrollmentAdapter,
)
from app.modules.training_schools.infrastructure.repository import (
    TrainingSchoolRepository,
)


class CreateTipoComplementario:
    def __init__(self, session: SessionDep) -> None:
        self.service = TrainingSchoolService(
            repository=TrainingSchoolRepository(session=session),
            enrollment=EnrollmentAdapter(session),
        )

    async def execute(
        self, nombre: str, sub_tipo_complementario: int | None
    ) -> TipoComplementarioInfo:
        return await self.service.create_tipo_complementario(
            nombre=nombre, sub_tipo_complementario=sub_tipo_complementario
        )
