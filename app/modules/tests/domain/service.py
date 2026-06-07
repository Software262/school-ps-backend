from app.modules.tests.application.contracts import EnrollmentDataService
from app.modules.tests.domain.entities import (
    ComplementarySummary,
    PeriodSummary,
    StudentSummary,
    TestDetailEntity,
)
from app.modules.tests.domain.repositories import InternalTestRepository
from app.modules.tests.schemas.request import (
    CreateTestDetailRequest,
    MassiveAssignmentRequest,
    PaymentRequest,
    UpdateTestDetailRequest,
)
from app.shared.schemas.filter_pagination_request import FilterPagination
from app.shared.utils.filter_pagination import calculate_offset


class InternalTestService:
    def __init__(
        self,
        repository: InternalTestRepository,
        enrollment: EnrollmentDataService,
    ):
        self.repository = repository
        self.enrollment = enrollment

    async def _build_test_entities(self, tests) -> list[TestDetailEntity]:
        if not tests:
            return []

        all_periodos = await self.enrollment.get_all_periodos()
        periodos_map = {p.id: p for p in all_periodos}

        students_cache: dict = {}
        comps_cache: dict = {}
        result = []

        for t in tests:
            if t.estudiante_id not in students_cache:
                students_cache[
                    t.estudiante_id
                ] = await self.enrollment.get_student_by_id(t.estudiante_id)
            if t.complementario_id not in comps_cache:
                comps_cache[
                    t.complementario_id
                ] = await self.enrollment.get_complementary_by_id(t.complementario_id)

            student = students_cache[t.estudiante_id]
            comp = comps_cache[t.complementario_id]

            if not student or not comp:
                continue

            periodo = periodos_map.get(t.periodo_id) if t.periodo_id else None

            result.append(
                TestDetailEntity(
                    id=t.id or 0,
                    estudiante_id=t.estudiante_id,
                    complementario_id=t.complementario_id,
                    tipo_prueba=t.tipo_prueba,
                    estado=t.estado,
                    valor_pagado=t.valor_pagado,
                    periodo_id=t.periodo_id,
                    created_at=t.created_at,
                    estudiante=StudentSummary(
                        nombre=student.nombre, documento=student.documento
                    ),
                    complementario=ComplementarySummary(
                        tipo_complementario=comp.tipo_complementario,
                        valor=comp.valor,
                    ),
                    periodo=PeriodSummary(id=periodo.id, nombre=periodo.nombre)
                    if periodo
                    else None,
                )
            )
        return result

    async def get_all_tests(self, filter_pagination: FilterPagination):
        offset = calculate_offset(filter_pagination.page, filter_pagination.limit)
        tests = await self.repository.get_tests_pagination(
            offset=offset, limit=filter_pagination.limit
        )
        return await self._build_test_entities(tests)

    async def get_test_by_id(self, test_id: int):
        return await self.repository.get_test_by_id(test_id)

    async def get_tests_by_student(
        self,
        student_id: int,
        filter_pagination: FilterPagination,
    ):
        offset = calculate_offset(filter_pagination.page, filter_pagination.limit)
        tests = await self.repository.get_tests_by_student(
            student_id=student_id,
            offset=offset,
            limit=filter_pagination.limit,
        )
        return await self._build_test_entities(tests)

    async def create_test(self, test_data: CreateTestDetailRequest):
        existing_assignments = await self.repository.get_existing_assignments(
            test_data.complementario_id, test_data.periodo_id
        )
        if test_data.estudiante_id in existing_assignments:
            raise ValueError("duplicate_assignment")
        return await self.repository.create_test(test_data)

    async def update_test(self, test_id: int, test_data: UpdateTestDetailRequest):
        test = await self.repository.get_test_by_id(test_id)
        if not test:
            return None
        return await self.repository.update_test(test=test, test_data=test_data)

    async def get_available_tests(self):
        return await self.enrollment.get_available_tests()

    async def get_all_grados(self):
        return await self.enrollment.get_all_grados()

    async def get_all_periodos(self):
        return await self.enrollment.get_all_periodos()

    async def get_all_estudiantes(self):
        return await self.enrollment.get_all_estudiantes()

    async def assign_massive(self, request: MassiveAssignmentRequest) -> dict:
        students = await self.enrollment.get_active_students_by_grade(request.grado_id)
        if not students:
            return {
                "assigned": [],
                "skipped": 0,
                "message": "No hay estudiantes activos en este grado",
            }

        existing_ids = await self.repository.get_existing_assignments(
            request.complementario_id, request.periodo_id
        )
        existing_set = set(existing_ids)

        new_students = [s for s in students if s.id not in existing_set]
        skipped = len(students) - len(new_students)

        if not new_students:
            return {
                "assigned": [],
                "skipped": skipped,
                "message": f"Todos los estudiantes ({skipped}) ya tienen esta prueba asignada",
            }

        reqs = [
            CreateTestDetailRequest(
                estudiante_id=s.id,
                complementario_id=request.complementario_id,
                tipo_prueba=request.tipo_prueba,
                estado="pendiente",
                valor_pagado=0,
                periodo_id=request.periodo_id,
            )
            for s in new_students
        ]

        assigned = await self.repository.assign_massive(reqs)
        return {
            "assigned": [{"id": a.id} for a in assigned],
            "skipped": skipped,
            "message": f"Se asignaron {len(assigned)} pruebas. {skipped} estudiante(s) ya la tenían.",
        }

    async def delete_test_complementary(self, comp_id: int) -> bool:
        comp = await self.enrollment.get_complementary_by_id(comp_id)
        if not comp:
            raise ValueError("Prueba no encontrada")
        await self.repository.delete_tests_by_complementary_id(comp_id)
        return await self.enrollment.delete_complementary(comp_id)

    async def update_test_complementary(
        self, comp_id: int, tipo_complementario: str, valor: int
    ) -> int:
        comp = await self.enrollment.get_complementary_by_id(comp_id)
        if not comp:
            raise ValueError("Prueba no encontrada")
        comp.tipo_complementario = tipo_complementario
        comp.valor = valor
        saved = await self.enrollment.save_complementary(comp)
        return saved.id

    async def delete_test(self, test_id: int) -> bool:
        test = await self.repository.get_test_by_id(test_id)
        if not test:
            raise ValueError("Test not found")
        return await self.repository.delete_test(test)

    async def register_test_payment(self, test_id: int, request: PaymentRequest):
        test = await self.repository.get_test_by_id(test_id)
        if not test:
            raise ValueError("Test not found")

        comp = await self.enrollment.get_complementary_by_id(test.complementario_id)
        if not comp:
            raise ValueError("Complementary not found")

        nuevo_total_pagado = (test.valor_pagado or 0) + request.monto
        if nuevo_total_pagado > comp.valor:
            raise ValueError(
                f"El monto a pagar no puede superar el saldo pendiente de la prueba. "
                f"Valor de la prueba: {comp.valor}. Pagado actualmente: {test.valor_pagado or 0}. "
                f"Intento de abono: {request.monto}."
            )

        test.valor_pagado = nuevo_total_pagado
        test.estado = "pagada" if test.valor_pagado >= comp.valor else "pago-parcial"

        return await self.repository.save_test(test)

    async def get_student_test_status(self, student_id: int):
        tests = await self.repository.get_tests_by_student(
            student_id=student_id, offset=0, limit=1000
        )
        entities = await self._build_test_entities(tests)
        has_pending = any(t.estado in ["pendiente", "pago-parcial"] for t in entities)
        return {"has_debt": has_pending, "tests": entities}
