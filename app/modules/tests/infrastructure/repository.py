from sqlmodel import select

from app.core.db import SessionDep
from app.modules.tests.domain.repositories import (
    InternalTestRepository as InternalTestRepositoryInterface,
)
from app.modules.tests.infrastructure.models import DetallePrueba
from app.modules.tests.schemas.request import (
    CreateTestDetailRequest,
    UpdateTestDetailRequest,
)


class InternalTestRepository(InternalTestRepositoryInterface):
    def __init__(self, session: SessionDep):
        self.session = session

    async def get_tests_pagination(
        self, offset: int, limit: int
    ) -> list[DetallePrueba]:
        return list(
            self.session.exec(select(DetallePrueba).offset(offset).limit(limit)).all()
        )

    async def get_test_by_id(self, test_id: int) -> DetallePrueba | None:
        return self.session.get(DetallePrueba, test_id)

    async def get_tests_by_student(
        self,
        student_id: int,
        offset: int,
        limit: int,
    ) -> list[DetallePrueba]:
        return list(
            self.session.exec(
                select(DetallePrueba)
                .where(DetallePrueba.estudiante_id == student_id)
                .offset(offset)
                .limit(limit)
            ).all()
        )

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
        tests = [
            DetallePrueba(
                estudiante_id=req.estudiante_id,
                complementario_id=req.complementario_id,
                tipo_prueba=req.tipo_prueba,
                estado=req.estado,
                valor_pagado=req.valor_pagado,
                periodo_id=req.periodo_id,
            )
            for req in requests
        ]
        self.session.add_all(tests)
        self.session.commit()
        for t in tests:
            self.session.refresh(t)
        return tests

    async def get_existing_assignments(
        self, complementario_id: int, periodo_id: int
    ) -> list[int]:
        results = self.session.exec(
            select(DetallePrueba.estudiante_id).where(
                DetallePrueba.complementario_id == complementario_id,
                DetallePrueba.periodo_id == periodo_id,
            )
        ).all()
        return [int(r) for r in results if r is not None]

    async def delete_test(self, test: DetallePrueba) -> bool:
        self.session.delete(test)
        self.session.commit()
        return True

    async def save_test(self, test: DetallePrueba) -> DetallePrueba:
        self.session.add(test)
        self.session.commit()
        self.session.refresh(test)
        return test

    async def delete_tests_by_complementary_id(self, comp_id: int) -> None:
        tests = self.session.exec(
            select(DetallePrueba).where(DetallePrueba.complementario_id == comp_id)
        ).all()
        for t in tests:
            self.session.delete(t)
        self.session.commit()
