from sqlmodel import col, select

from app.core.db import SessionDep
from app.modules.classroom.application.contracts import (
    ClassroomEnrollmentService,
)
from app.modules.classroom.domain.entities import (
    GradeEntity,
    StudentEntity,
)
from app.modules.enrollment.infrastructure.models import (
    Docente,
    Estudiante,
    Grado,
)


class ClassroomEnrollmentAdapter(ClassroomEnrollmentService):
    def __init__(self, session: SessionDep):
        self.session = session

    def get_student_by_document(self, documento: str) -> StudentEntity | None:
        statement = select(Estudiante).where(col(Estudiante.documento) == documento)

        result = self.session.exec(statement).first()

        if result is None or result.id is None:
            return None

        return StudentEntity(
            id=result.id,
            nombre=result.nombre,
            documento=result.documento,
            grado_id=result.grado_id,
        )

    def get_students_by_grade(self, grado_id: int) -> list[StudentEntity]:
        statement = select(Estudiante).where(col(Estudiante.grado_id) == grado_id)

        results = self.session.exec(statement).all()

        return [
            StudentEntity(
                id=e.id or 0,
                nombre=e.nombre,
                documento=e.documento,
                grado_id=e.grado_id,
            )
            for e in results
            if e.id is not None
        ]

    def get_grade(self, grado_id: int) -> GradeEntity | None:
        statement = select(Grado).where(col(Grado.id) == grado_id)

        grado = self.session.exec(statement).first()

        if grado is None or grado.id is None:
            return None

        docente_nombre = None

        if grado.docente_titular_id is not None:
            docente = self.session.get(
                Docente,
                grado.docente_titular_id,
            )

            if docente is not None:
                docente_nombre = docente.nombre

        return GradeEntity(
            id=grado.id,
            nombre=grado.nombre,
            docente_titular=docente_nombre,
        )

    def get_all_grades(self) -> list[GradeEntity]:
        statement = select(Grado).order_by(col(Grado.nombre))

        grados = self.session.exec(statement).all()

        resultado: list[GradeEntity] = []

        for grado in grados:
            if grado.id is None:
                continue

            docente_nombre = None

            if grado.docente_titular_id is not None:
                docente = self.session.get(
                    Docente,
                    grado.docente_titular_id,
                )

                if docente is not None:
                    docente_nombre = docente.nombre

            resultado.append(
                GradeEntity(
                    id=grado.id,
                    nombre=grado.nombre,
                    docente_titular=docente_nombre,
                )
            )

        return resultado
