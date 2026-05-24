from app.core.db import SessionDep
from app.modules.enrollment.domain.service import EnrollmentService
from app.modules.enrollment.infrastructure.repository import (
    SQLEnrollmentRepository,
)


class AssignComplementary:
    """Caso de uso: asignar un complementario a una matrícula existente."""

    def __init__(self, session: SessionDep) -> None:
        repository = SQLEnrollmentRepository(session)
        self._service = EnrollmentService(repository)

    def execute(
        self,
        matricula_id: int,
        complementary_id: int,
        descuento: int,
    ) -> int:
        return self._service.assign_complementary(
            matricula_id=matricula_id,
            complementary_id=complementary_id,
            descuento=descuento,
        )
