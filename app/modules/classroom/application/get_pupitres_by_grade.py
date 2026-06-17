from app.core.db import SessionDep
from app.modules.classroom.infrastructure.repository import PupitreRepositoryImpl
from app.modules.classroom.infrastructure.enrollment_adapter import (
    ClassroomEnrollmentAdapter,
)
from app.modules.classroom.domain.service import PupitreService
from app.modules.classroom.schemas.response import PupitreStudentOutSchema


class GetPupitresByGrade:
    def __init__(self, session: SessionDep):
        self.repository = PupitreRepositoryImpl(session=session)
        self.students_provider = ClassroomEnrollmentAdapter(session=session)
        self.service = PupitreService(
            repositorio=self.repository,
            enrollment_service=self.students_provider,
        )

    async def execute(self, grado_id: int) -> list[PupitreStudentOutSchema] | None:
        estudiantes = self.students_provider.get_students_by_grade(grado_id)
        if not estudiantes:
            return None
        estudiantes_map = {e.id: e for e in estudiantes}
        estudiante_ids = list(estudiantes_map.keys())

        pupitres = await self.service.get_desks_by_students(estudiante_ids)
        if not pupitres:
            return None

        grado = self.students_provider.get_grade(grado_id)

        return [
            PupitreStudentOutSchema(
                id=pupitre.id,
                estudiante_id=pupitre.estudiante_id,
                nombre_estudiante=estudiantes_map[pupitre.estudiante_id].nombre,
                documento=estudiantes_map[pupitre.estudiante_id].documento,
                grado=grado.nombre if grado else "Sin grado",
                docente_titular=grado.docente_titular if grado else None,
                estado=pupitre.estado,
                observacion=pupitre.observacion,
            )
            for pupitre in pupitres
        ]
