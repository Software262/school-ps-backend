from app.core.db import SessionDep
from app.modules.classroom.infrastructure.repository import PupitreRepositoryImpl
from app.modules.classroom.infrastructure.enrollment_adapter import (
    ClassroomEnrollmentAdapter,
)
from app.modules.classroom.domain.service import PupitreService
from app.modules.classroom.schemas.response import PupitreStudentOutSchema


class GetPupitreByStudent:
    def __init__(self, session: SessionDep):
        self.repository = PupitreRepositoryImpl(session=session)
        self.service = PupitreService(repositorio=self.repository)
        self.student_provider = ClassroomEnrollmentAdapter(session=session)

    async def execute(
        self, documento_estudiante: str
    ) -> PupitreStudentOutSchema | None:
        estudiante = self.student_provider.get_student_by_document(documento_estudiante)
        if not estudiante:
            return None

        pupitre = await self.service.get_desk_by_student(estudiante.id)
        if not pupitre:
            return None

        grado = self.student_provider.get_grade(estudiante.grado_id)

        return PupitreStudentOutSchema(
            id=pupitre.id,
            estudiante_id=estudiante.id,
            nombre_estudiante=estudiante.nombre,
            documento=estudiante.documento,
            grado=grado.nombre if grado else "Sin grado",
            docente_titular=grado.docente_titular if grado else None,
            estado_pupitre=pupitre.estado_pupitre,
            observacion=pupitre.observacion,
        )
