from app.core.db import SessionDep
from app.modules.training_schools.domain.service import TrainingSchoolService
from app.modules.training_schools.infrastructure.enrollment_adapter import (
    EnrollmentAdapter,
)
from app.modules.training_schools.infrastructure.repository import (
    TrainingSchoolRepository,
)
from app.modules.training_schools.schemas.response import EnrollmentDetailResponse


class GetEnrollmentsDetail:
    def __init__(self, session: SessionDep) -> None:
        self.service = TrainingSchoolService(
            repository=TrainingSchoolRepository(session=session),
            enrollment=EnrollmentAdapter(session),
        )

    async def execute(self, periodo_id: int) -> list[EnrollmentDetailResponse]:
        pairs = await self.service.get_enrollments_with_students(periodo_id)
        return [
            EnrollmentDetailResponse(
                id=enr.id,
                complementario_id=enr.complementario_id,
                estudiante_id=enr.estudiante_id,
                estudiante_nombre=student.nombre,
                estudiante_documento=student.documento,
                estudiante_grado=student.grado_nombre,
                periodo_id=enr.periodo_id,
                usuario_id=enr.usuario_id,
                fecha_registro=enr.fecha_registro,
                mes=enr.mes,
                activo=enr.activo,
                estado_escuela=enr.estado_escuela,
                saldo_pendiente=enr.saldo_pendiente,
                motivo_retiro=enr.motivo_retiro,
                observaciones=enr.observaciones,
                valor_acordado=enr.valor_acordado,
                numero_comprobante=enr.numero_comprobante,
                created_at=enr.created_at,
                updated_at=enr.updated_at,
            )
            for enr, student in pairs
            if enr.id is not None
        ]
