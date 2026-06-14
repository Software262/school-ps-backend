from sqlmodel import col, or_, select

from app.core.db import SessionDep
from app.modules.enrollment.infrastructure.models import (
    Complementario,
    Estudiante,
    Grado,
    Periodo,
    TipoComplementario,
)
from app.modules.tests.application.contracts import EnrollmentDataService
from app.modules.tests.domain.entities import (
    ComplementarioEntity,
    EstudianteEntity,
    GradoEntity,
    PeriodoEntity,
)


class EnrollmentAdapter(EnrollmentDataService):
    """Adapter that implements EnrollmentDataService using enrollment's DB models."""

    def __init__(self, session: SessionDep):
        self.session = session

    async def get_all_grados(self) -> list[GradoEntity]:
        grados = self.session.exec(select(Grado)).all()

        return [GradoEntity(id=g.id or 0, nombre=g.nombre) for g in grados]

    async def get_all_periodos(self) -> list[PeriodoEntity]:
        periodos = self.session.exec(select(Periodo).where(Periodo.estado)).all()

        return [
            PeriodoEntity(
                id=p.id or 0,
                nombre=f"{p.periodo_electivo.year}-{str(p.periodo_electivo.month).zfill(2)}",
                fecha=str(p.fecha.date()),
            )
            for p in periodos
        ]

    async def get_all_estudiantes(self) -> list[EstudianteEntity]:
        students = self.session.exec(select(Estudiante).where(Estudiante.activo)).all()

        return [
            EstudianteEntity(
                id=s.id or 0,
                nombre=s.nombre,
                documento=s.documento,
                grado_id=s.grado_id,
            )
            for s in students
        ]

    async def get_active_students_by_grade(
        self, grado_id: int
    ) -> list[EstudianteEntity]:
        results = self.session.exec(
            select(Estudiante)
            .where(Estudiante.grado_id == grado_id)
            .where(Estudiante.activo)
        ).all()

        return [
            EstudianteEntity(
                id=s.id or 0,
                nombre=s.nombre,
                documento=s.documento,
                grado_id=s.grado_id,
            )
            for s in results
        ]

    async def get_student_by_id(self, student_id: int) -> EstudianteEntity | None:
        student = self.session.get(Estudiante, student_id)
        if not student:
            return None

        return EstudianteEntity(
            id=student.id or 0,
            nombre=student.nombre,
            documento=student.documento,
            grado_id=student.grado_id,
        )

    async def get_available_tests(self) -> list[ComplementarioEntity]:
        matricula_type = self.session.exec(
            select(TipoComplementario).where(TipoComplementario.nombre == "Matricula")
        ).first()

        stmt = select(Complementario).where(
            Complementario.estado_complemento == "Activo"
        )

        if matricula_type and matricula_type.id is not None:
            matricula_ids = self.session.exec(
                select(col(TipoComplementario.id)).where(
                    or_(
                        TipoComplementario.id == matricula_type.id,
                        TipoComplementario.sub_tipo_complementario == matricula_type.id,
                    )
                )
            ).all()
            stmt = stmt.where(
                col(Complementario.tipo_complementario_id).not_in(matricula_ids)
            )

        results = self.session.exec(stmt).all()
        return [
            ComplementarioEntity(
                id=c.id or 0,
                tipo_complementario=c.nombre,
                valor=c.valor,
                anio=c.anio,
            )
            for c in results
        ]

    async def get_complementary_by_id(
        self, comp_id: int
    ) -> ComplementarioEntity | None:
        comp = self.session.get(Complementario, comp_id)

        if not comp:
            return None

        return ComplementarioEntity(
            id=comp.id or 0,
            tipo_complementario=comp.nombre,
            valor=comp.valor,
            anio=comp.anio,
        )

    async def save_complementary(
        self, comp: ComplementarioEntity
    ) -> ComplementarioEntity:
        model = self.session.get(Complementario, comp.id)

        if model:
            model.nombre = comp.tipo_complementario
            model.valor = comp.valor
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)

            return ComplementarioEntity(
                id=model.id or 0,
                tipo_complementario=model.nombre,
                valor=model.valor,
                anio=model.anio,
            )

        return comp

    async def delete_complementary(self, comp_id: int) -> bool:
        comp = self.session.get(Complementario, comp_id)

        if not comp:
            return False

        self.session.delete(comp)
        self.session.commit()

        return True
