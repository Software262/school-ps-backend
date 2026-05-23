import pytest

from types import SimpleNamespace

from app.modules.training_schools.domain.service import TrainingSchoolsService


class MockRepo:
    def __init__(self, student=None, program=None, enrollment=None):
        self._student = student
        self._program = program
        self._enrollment = enrollment

    async def get_student_by_id(self, student_id: int):
        return self._student

    async def get_complementario_by_id(self, complementario_id: int):
        return self._program

    async def get_enrollment(self, student_id: int, complementario_id: int, mes: str):
        return self._enrollment

    async def create_enrollment(self, enrollment_data):
        return SimpleNamespace(
            id=1,
            complementario_id=enrollment_data.complementario_id,
            estudiante_id=enrollment_data.estudiante_id,
            fecha_registro=None,
            mes=enrollment_data.mes,
            activo=True,
            estado_escuela=False,
        )

    async def save_enrollment(self, enrollment):
        return enrollment

    async def get_student_enrollments(self, student_id: int):
        return [self._enrollment] if self._enrollment else []

    async def get_enrollments_by_program(self, complementario_id: int):
        return [self._enrollment] if self._enrollment else []


@pytest.mark.asyncio
async def test_enroll_student_success():
    student = SimpleNamespace(id=1)
    program = SimpleNamespace(id=2, estado_complemento="activo")

    class Req:
        estudiante_id = 1
        complementario_id = 2
        mes = "Mayo"

    repo = MockRepo(student=student, program=program, enrollment=None)
    service = TrainingSchoolsService(repository=repo)

    result = await service.enroll_student(Req)
    assert result is not None
    assert result.estudiante_id == Req.estudiante_id


@pytest.mark.asyncio
async def test_enroll_student_duplicate():
    student = SimpleNamespace(id=1)
    program = SimpleNamespace(id=2, estado_complemento="activo")
    enrollment = SimpleNamespace(id=3)

    class Req:
        estudiante_id = 1
        complementario_id = 2
        mes = "Mayo"

    repo = MockRepo(student=student, program=program, enrollment=enrollment)
    service = TrainingSchoolsService(repository=repo)

    result = await service.enroll_student(Req)
    assert result is None


@pytest.mark.asyncio
async def test_register_payment_success():
    enrollment = SimpleNamespace(id=1, activo=True, estado_escuela=False, complementario_id=2, estudiante_id=1, mes="Mayo")
    repo = MockRepo(enrollment=enrollment)
    service = TrainingSchoolsService(repository=repo)

    class Req:
        estudiante_id = 1
        complementario_id = 2
        mes = "Mayo"

    result = await service.register_payment(Req)
    assert result is not None
    assert result.estado_escuela is True


@pytest.mark.asyncio
async def test_register_payment_no_enrollment():
    repo = MockRepo(enrollment=None)
    service = TrainingSchoolsService(repository=repo)

    class Req:
        estudiante_id = 1
        complementario_id = 2
        mes = "Mayo"

    result = await service.register_payment(Req)
    assert result is None


@pytest.mark.asyncio
async def test_unsubscribe_student():
    enrollment = SimpleNamespace(id=1, activo=True, estado_escuela=False, complementario_id=2, estudiante_id=1, mes="Mayo")
    repo = MockRepo(enrollment=enrollment)
    service = TrainingSchoolsService(repository=repo)

    result = await service.unsubscribe_student(1, 2, "Mayo", SimpleNamespace(motivo="Motivo"))
    assert result is not None
    assert result.activo is False
    assert result.motivo_baja == "Motivo"


@pytest.mark.asyncio
async def test_get_student_status_nonexistent():
    repo = MockRepo(student=None, enrollment=None)
    service = TrainingSchoolsService(repository=repo)

    result = await service.get_student_status(999)
    # Expect a dictionary indicating the student does not exist and paz_y_salvo False
    assert isinstance(result, dict)
    assert result.get("paz_y_salvo") is False
