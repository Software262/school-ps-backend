from sqlmodel import select, col

from app.core.db import SessionDep
from app.modules.tests.domain.repositories import (
    InternalTestRepository as InternalTestRepositoryInterface,
)
from app.modules.tests.infrastructure.models import DetallePrueba
from app.modules.tests.schemas.request import (
    CreateTestDetailRequest,
    UpdateTestDetailRequest,
)
from app.modules.enrollment.infrastructure.models import (
    Estudiante,
    Complementario,
    Periodo,
    Grado,
)
from app.modules.tests.domain.entities import (
    TestDetailEntity,
    StudentSummary,
    ComplementarySummary,
    PeriodSummary,
    GradoEntity,
    PeriodoEntity,
    EstudianteEntity,
)


class InternalTestRepository(InternalTestRepositoryInterface):
    def __init__(self, session: SessionDep):
        self.session = session

    async def get_tests_pagination(
        self, offset: int, limit: int
    ) -> list[TestDetailEntity]:
        stmt = (
            select(DetallePrueba, Estudiante, Complementario, Periodo)
            .join(Estudiante)
            .join(Complementario)
            .outerjoin(Periodo)
            .offset(offset)
            .limit(limit)
        )
        results = self.session.exec(stmt).all()
        return [
            TestDetailEntity(
                id=d.id or 0,
                estudiante_id=d.estudiante_id,
                complementario_id=d.complementario_id,
                tipo_prueba=d.tipo_prueba,
                estado=d.estado,
                valor_pagado=d.valor_pagado,
                periodo_id=d.periodo_id,
                created_at=d.created_at,
                estudiante=StudentSummary(nombre=e.nombre, documento=e.documento),
                complementario=ComplementarySummary(
                    tipo_complementario=c.tipo_complementario,
                    valor=c.valor,
                ),
                periodo=PeriodSummary(
                    id=p.id or 0,
                    nombre=str(p.periodo_electivo.year)
                    + "-"
                    + str(p.periodo_electivo.month).zfill(2),
                )
                if p
                else None,
            )
            for d, e, c, p in results
        ]

    async def get_test_by_id(self, test_id: int) -> DetallePrueba | None:
        return self.session.get(DetallePrueba, test_id)

    async def get_tests_by_student(
        self,
        student_id: int,
        offset: int,
        limit: int,
    ) -> list[TestDetailEntity]:
        stmt = (
            select(DetallePrueba, Estudiante, Complementario)
            .join(Estudiante)
            .join(Complementario)
            .where(DetallePrueba.estudiante_id == student_id)
            .offset(offset)
            .limit(limit)
        )
        results = self.session.exec(stmt).all()
        return [
            TestDetailEntity(
                id=d.id or 0,
                estudiante_id=d.estudiante_id,
                complementario_id=d.complementario_id,
                tipo_prueba=d.tipo_prueba,
                estado=d.estado,
                valor_pagado=d.valor_pagado,
                created_at=d.created_at,
                estudiante=StudentSummary(nombre=e.nombre, documento=e.documento),
                complementario=ComplementarySummary(
                    tipo_complementario=c.tipo_complementario,
                    valor=c.valor,
                ),
            )
            for d, e, c in results
        ]

    async def create_test(self, test_data: CreateTestDetailRequest) -> DetallePrueba:
        new_test = DetallePrueba(
            estudiante_id=test_data.estudiante_id,
            complementario_id=test_data.complementario_id,
            tipo_prueba=test_data.tipo_prueba,
            estado=test_data.estado,
            valor_pagado=test_data.valor_pagado,
            periodo_id=test_data.periodo_id,
        )

        self.session.add(new_test)
        self.session.commit()
        self.session.refresh(new_test)

        return new_test

    async def update_test(
        self,
        test: DetallePrueba,
        test_data: UpdateTestDetailRequest,
    ) -> DetallePrueba:
        test.estudiante_id = test_data.estudiante_id
        test.complementario_id = test_data.complementario_id
        test.tipo_prueba = test_data.tipo_prueba
        test.estado = test_data.estado
        test.valor_pagado = test_data.valor_pagado
        test.periodo_id = test_data.periodo_id

        self.session.add(test)
        self.session.commit()
        self.session.refresh(test)

        return test

    async def assign_massive(
        self, requests: list[CreateTestDetailRequest]
    ) -> list[DetallePrueba]:
        tests = []
        for req in requests:
            tests.append(
                DetallePrueba(
                    estudiante_id=req.estudiante_id,
                    complementario_id=req.complementario_id,
                    tipo_prueba=req.tipo_prueba,
                    estado=req.estado,
                    valor_pagado=req.valor_pagado,
                    periodo_id=req.periodo_id,
                )
            )
        self.session.add_all(tests)
        self.session.commit()
        for t in tests:
            self.session.refresh(t)
        return tests

    async def get_active_students_by_grade(self, grado_id: int) -> list[Estudiante]:
        results = self.session.exec(
            select(Estudiante)
            .where(Estudiante.grado_id == grado_id)
            .where(Estudiante.activo)
        ).all()
        return list(results)

    async def get_available_tests(self) -> list[Complementario]:
        results = self.session.exec(
            select(Complementario)
            .where(Complementario.estado_complemento == "Activo")
            .where(col(Complementario.uso_matricula).is_(False))
        ).all()
        return list(results)

    async def get_existing_assignments(
        self, complementario_id: int, periodo_id: int
    ) -> list[int]:
        results = self.session.exec(
            select(DetallePrueba.estudiante_id).where(
                DetallePrueba.complementario_id == complementario_id,
                DetallePrueba.periodo_id == periodo_id,
            )
        ).all()
        # Handle cases where estudiante_id could be None, though typically it's an int
        return [int(r) for r in results if r is not None]

    async def get_complementary_by_id(self, comp_id: int) -> Complementario | None:
        return self.session.get(Complementario, comp_id)

    async def delete_test_complementary(self, comp_id: int) -> bool:
        comp = self.session.get(Complementario, comp_id)
        if not comp:
            return False

        detalles = self.session.exec(
            select(DetallePrueba).where(DetallePrueba.complementario_id == comp_id)
        ).all()
        for d in detalles:
            self.session.delete(d)

        self.session.delete(comp)
        self.session.commit()
        return True

    async def save_complementary(self, comp: Complementario) -> Complementario:
        self.session.add(comp)
        self.session.commit()
        self.session.refresh(comp)
        return comp

    async def delete_test(self, test: DetallePrueba) -> bool:
        self.session.delete(test)
        self.session.commit()
        return True

    async def save_test(self, test: DetallePrueba) -> DetallePrueba:
        self.session.add(test)
        self.session.commit()
        self.session.refresh(test)
        return test

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
