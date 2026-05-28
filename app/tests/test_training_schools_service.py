import pytest

from types import SimpleNamespace
from typing import Any, Sequence

from app.modules.training_schools.domain.repositories import TrainingSchoolsRepository
from app.modules.training_schools.domain.service import TrainingSchoolsService
from app.modules.training_schools.schemas.request import (
    CreateEnrollmentRequest,
    CreateProgramRequest,
    RegisterPaymentRequest,
    UnsubscribeRequest,
)


class MockRepo(TrainingSchoolsRepository):
    def __init__(self, student=None, program=None, enrollment=None):
        self._student = student
        self._program = program
        self._enrollment = enrollment

    async def get_student_by_id(self, student_id: int) -> Any:
        return self._student

    async def search_students(self, query: str) -> Sequence[Any]:
        return [self._student] if self._student else []

    async def get_complementario_by_id(self, complementario_id: int) -> Any:
        return self._program

    async def get_available_programs(self) -> Sequence[Any]:
        return [self._program] if self._program else []

    async def get_program_by_name(self, nombre: str) -> Any:
        return self._program

    async def create_program(self, data: Any) -> Any:
        return SimpleNamespace(
            id=1,
            tipo_complementario=data.nombre,
            anio=2026,
            valor=data.valor,
            estado_complemento="activo",
            uso_matricula=False,
        )

    async def get_enrollment(
        self, student_id: int, complementario_id: int, mes: str
    ) -> Any:
        return self._enrollment

    async def create_enrollment(self, enrollment_data: Any) -> Any:
        return SimpleNamespace(
            id=1,
            complementario_id=enrollment_data.complementario_id,
            estudiante_id=enrollment_data.estudiante_id,
            fecha_registro=None,
            mes=enrollment_data.mes,
            activo=True,
            estado_escuela=False,
            updated_at=None,
        )

    async def save_enrollment(self, enrollment: Any) -> Any:
        return enrollment

    async def get_student_enrollments(self, student_id: int) -> Sequence[Any]:
        return [self._enrollment] if self._enrollment else []

    async def get_enrollments_by_program(self, complementario_id: int) -> Sequence[Any]:
        return [self._enrollment] if self._enrollment else []

    async def get_enrollments(
        self,
        student_id=None,
        complementario_id=None,
        mes=None,
        activo=None,
        estado_escuela=None,
    ) -> Sequence[Any]:
        return [self._enrollment] if self._enrollment else []


@pytest.mark.asyncio
async def test_enroll_student_success():
    student = SimpleNamespace(id=1)
    program = SimpleNamespace(id=2, estado_complemento="activo")
    repo = MockRepo(student=student, program=program, enrollment=None)
    service = TrainingSchoolsService(repository=repo)
    request = CreateEnrollmentRequest(estudiante_id=1, complementario_id=2, mes="Mayo")

    result = await service.enroll_student(request)

    assert result is not None
    assert result.estudiante_id == request.estudiante_id


@pytest.mark.asyncio
async def test_search_students():
    student = SimpleNamespace(
        id=1, nombre="Estudiante Prueba", documento="123456789", activo=True
    )
    repo = MockRepo(student=student)
    service = TrainingSchoolsService(repository=repo)

    result = await service.search_students("Prueba")

    assert len(result) == 1
    assert result[0].documento == "123456789"


@pytest.mark.asyncio
async def test_list_available_programs():
    program = SimpleNamespace(id=2, estado_complemento="activo")
    repo = MockRepo(program=program)
    service = TrainingSchoolsService(repository=repo)

    result = await service.list_available_programs()

    assert len(result) == 1
    assert result[0].id == 2


@pytest.mark.asyncio
async def test_create_program_success():
    repo = MockRepo(program=None)
    service = TrainingSchoolsService(repository=repo)

    result = await service.create_program(
        CreateProgramRequest(nombre="Teatro", valor=30000)
    )

    assert result is not None
    assert result.tipo_complementario == "Teatro"


@pytest.mark.asyncio
async def test_enroll_student_duplicate():
    student = SimpleNamespace(id=1)
    program = SimpleNamespace(id=2, estado_complemento="activo")
    enrollment = SimpleNamespace(id=3)
    repo = MockRepo(student=student, program=program, enrollment=enrollment)
    service = TrainingSchoolsService(repository=repo)
    request = CreateEnrollmentRequest(estudiante_id=1, complementario_id=2, mes="Mayo")

    result = await service.enroll_student(request)

    assert result is None


@pytest.mark.asyncio
async def test_register_payment_success():
    enrollment = SimpleNamespace(
        id=1,
        activo=True,
        estado_escuela=False,
        complementario_id=2,
        estudiante_id=1,
        mes="Mayo",
        updated_at=None,
    )
    repo = MockRepo(enrollment=enrollment)
    service = TrainingSchoolsService(repository=repo)
    request = RegisterPaymentRequest(estudiante_id=1, complementario_id=2, mes="Mayo")

    result = await service.register_payment(request)

    assert result is not None
    assert result.estado_escuela is True


@pytest.mark.asyncio
async def test_unmark_payment_success():
    enrollment = SimpleNamespace(
        id=1,
        activo=True,
        estado_escuela=True,
        complementario_id=2,
        estudiante_id=1,
        mes="Mayo",
        updated_at=None,
    )
    repo = MockRepo(enrollment=enrollment)
    service = TrainingSchoolsService(repository=repo)
    request = RegisterPaymentRequest(estudiante_id=1, complementario_id=2, mes="Mayo")

    result = await service.unmark_payment(request)

    assert result is not None
    assert result.estado_escuela is False


@pytest.mark.asyncio
async def test_register_payment_no_enrollment():
    repo = MockRepo(enrollment=None)
    service = TrainingSchoolsService(repository=repo)
    request = RegisterPaymentRequest(estudiante_id=1, complementario_id=2, mes="Mayo")

    result = await service.register_payment(request)

    assert result is None


@pytest.mark.asyncio
async def test_unsubscribe_student():
    enrollment = SimpleNamespace(
        id=1,
        activo=True,
        estado_escuela=False,
        complementario_id=2,
        estudiante_id=1,
        mes="Mayo",
        updated_at=None,
    )
    repo = MockRepo(enrollment=enrollment)
    service = TrainingSchoolsService(repository=repo)

    result = await service.unsubscribe_student(
        1, 2, "Mayo", UnsubscribeRequest(motivo="Motivo")
    )

    assert result is not None
    assert result.activo is False
    assert result.motivo_baja == "Motivo"


@pytest.mark.asyncio
async def test_get_student_status_nonexistent():
    repo = MockRepo(student=None, enrollment=None)
    service = TrainingSchoolsService(repository=repo)

    result = await service.get_student_status(999)

    assert isinstance(result, dict)
    assert result.get("paz_y_salvo") is False


@pytest.mark.asyncio
async def test_get_monthly_status_with_pending_month():
    enrollment = SimpleNamespace(
        id=1,
        activo=True,
        estado_escuela=False,
        complementario_id=2,
        estudiante_id=1,
        mes="febrero",
        updated_at=None,
    )
    repo = MockRepo(enrollment=enrollment)
    service = TrainingSchoolsService(repository=repo)

    result = await service.get_monthly_status(1, 2)

    assert result["paz_y_salvo"] is False
    assert "febrero" in result["detalle"]


@pytest.mark.asyncio
async def test_unsubscribe_student_from_program_marks_active_records_inactive():
    enrollment = SimpleNamespace(
        id=1,
        activo=True,
        estado_escuela=True,
        complementario_id=2,
        estudiante_id=1,
        mes="marzo",
        updated_at=None,
    )
    repo = MockRepo(enrollment=enrollment)
    service = TrainingSchoolsService(repository=repo)

    result = await service.unsubscribe_student_from_program(
        1, 2, UnsubscribeRequest(motivo="Retiro voluntario")
    )

    assert len(result) == 1
    assert result[0].activo is False
    assert result[0].motivo_baja == "Retiro voluntario"
