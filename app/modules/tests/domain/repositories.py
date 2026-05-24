from sqlmodel import select

from app.core.db import SessionDep
from app.modules.tests.infrastructure.models import DetallePrueba
from app.modules.tests.schemas.request import (
    CreateTestDetailRequest,
    UpdateTestDetailRequest,
)


class InternalTestRepository:
    def __init__(self, session: SessionDep):
        self.session = session

    async def get_tests_pagination(self, offset: int, limit: int):
        return self.session.exec(
            select(DetallePrueba).offset(offset).limit(limit)
        ).all()

    async def get_test_by_id(self, test_id: int):
        return self.session.get(DetallePrueba, test_id)

    async def get_tests_by_student(
        self, student_id: int, offset: int, limit: int,
    ):
        return self.session.exec(
            select(DetallePrueba)
            .where(DetallePrueba.estudiante_id == student_id)
            .offset(offset)
            .limit(limit)
        ).all()

    async def create_test(self, test_data: CreateTestDetailRequest):
        new_test = DetallePrueba(
            estudiante_id=test_data.estudiante_id,
            complementario_id=test_data.complementario_id,
            tipo_prueba=test_data.tipo_prueba,
            estado=test_data.estado,
        )

        self.session.add(new_test)
        self.session.commit()
        self.session.refresh(new_test)

        return new_test

    async def update_test(
        self, test: DetallePrueba, test_data: UpdateTestDetailRequest,
    ):
        test.estudiante_id = test_data.estudiante_id
        test.complementario_id = test_data.complementario_id
        test.tipo_prueba = test_data.tipo_prueba
        test.estado = test_data.estado

        self.session.add(test)
        self.session.commit()
        self.session.refresh(test)

        return test
