from abc import ABC, abstractmethod

from app.modules.enrollment.domain.entities import (
    ComplementaryDetail,
    GradeInfo,
    StudentGeneralInfo,
    StudentInfo,
    ComplementaryConcept,
)
from app.modules.enrollment.infrastructure.models import (
    Complementario,
    Estudiante,
    Pago,
    Periodo,
)


class EnrollmentRepository(ABC):
    """Interfaz abstracta para el acceso a datos de matrícula."""

    # === Consulta ===

    @abstractmethod
    def get_student_by_id(self, student_id: int) -> StudentInfo | None:
        """Obtiene la información del estudiante con su grado."""
        ...

    @abstractmethod
    def get_enrollment_base_cost(self, grade_id: int, year: int) -> int | None:
        """Obtiene el costo base de matrícula para un grado y año."""
        ...

    @abstractmethod
    def get_enrollment_details(
        self, student_id: int, year: int
    ) -> tuple[int | None, str, list[ComplementaryDetail], int, int]:
        """
        Obtiene los detalles de matrícula de un estudiante para un año.

        Returns:
            Tuple de (matricula_id, estado_matricula, lista_complementarios,
                       pendiente_base, valor_total).
            Si no existe matrícula, retorna (None, 'pendiente', [], 0, 0).
        """
        ...

    # === Registro de matrícula ===

    @abstractmethod
    def get_param_matricula_id(self, grade_id: int, year: int) -> int | None:
        """Obtiene el ID del registro ParametrizarMatricula para un grado y año."""
        ...

    @abstractmethod
    def student_has_enrollment(self, student_id: int, year: int) -> bool:
        """Verifica si el estudiante ya tiene matrícula para el año dado."""
        ...

    @abstractmethod
    def get_active_complementaries(self, year: int) -> list[tuple[int, str, int]]:
        """
        Obtiene los complementarios activos del tipo Matricula para un año.

        Returns:
            Lista de (complementario_id, nombre, valor).
        """
        ...

    @abstractmethod
    def period_exists(self, period_id: int) -> bool:
        """Verifica si un periodo existe en la base de datos."""
        ...

    @abstractmethod
    def find_active_period_by_year(self, year: int) -> int | None:
        """Busca el ID del periodo académico activo correspondiente al año dado."""
        ...

    @abstractmethod
    def get_or_create_matricula_tipo_id(self) -> int:
        """Busca o crea el ID del tipo de complementario 'Matricula'."""
        ...



    @abstractmethod
    def create_enrollment(
        self,
        para_matricula_id: int,
        student_id: int,
        period_id: int,
        valor_total: int,
        base_cost: int,
        complementary_details: list[tuple[int, int]],
    ) -> tuple[int, list[int]]:
        """
        Crea el registro de matrícula con sus detalles.

        Args:
            para_matricula_id: ID del ParametrizarMatricula.
            student_id: ID del estudiante.
            period_id: ID del periodo.
            valor_total: Valor total de la matrícula.
            base_cost: Costo base pendiente.
            complementary_details: Lista de (complementario_id, valor).

        Returns:
            Tuple: (ID de la matrícula creada, lista de IDs de los detalles creados).
        """
        ...

    # === Pagos ===

    @abstractmethod
    def get_enrollment_by_id(self, matricula_id: int) -> tuple | None:
        """
        Obtiene matrícula por ID con sus pendientes.

        Returns:
            Tuple (id, estudiante_id, valor_total, estado_matricula,
                   pendiente_base, para_matricula_id)
            o None si no existe.
        """
        ...

    @abstractmethod
    def get_enrollment_complementary_details(
        self, matricula_id: int
    ) -> list[tuple[int, int, str, int, int, int]]:
        """
        Obtiene los detalles de complementarios de una matrícula con pendientes > 0.

        Returns:
            Lista de (detalle_id, complementario_id, tipo, valor_pendiente).
        """
        ...

    @abstractmethod
    def validate_talonario_unique(self, codigo: str) -> bool:
        """Verifica que el código de talonario no esté ya registrado."""
        ...

    @abstractmethod
    def create_payment(
        self,
        matricula_id: int,
        codigo_talonario: str,
        monto_total: int,
        observacion: str | None,
        distribuciones: list[tuple[str, int | None, int]],
    ) -> int:
        """
        Crea el registro de pago con su desglose.

        Args:
            distribuciones: Lista de (concepto, complementario_id, monto_aplicado).

        Returns:
            ID del pago creado.
        """
        ...

    @abstractmethod
    def update_pending_base(self, matricula_id: int, new_pending: int) -> None:
        """Actualiza el valor_pendiente_base de una matrícula."""
        ...

    @abstractmethod
    def update_complementary_pending(
        self,
        matricula_id: int,
        complementario_id: int,
        new_pending: int,
        detalle_id: int | None = None,
    ) -> None:
        """Actualiza el valor_pendiente de un detalle_matricula."""
        ...

    @abstractmethod
    def update_enrollment_status(self, matricula_id: int, status: str) -> None:
        """Actualiza el estado_matricula (pendiente / parcial / paz_y_salvo)."""
        ...

    @abstractmethod
    def enrollment_has_payments(self, matricula_id: int) -> bool:
        """Retorna True si existe al menos un pago registrado para esta matrícula."""
        ...

    # === Complementarios ===

    @abstractmethod
    def create_complementary(
        self,
        nombre: str,
        tipo_complementario_id: int,
        anio: int,
        valor: int,
        estado: str,
    ) -> int:
        """Crea un nuevo concepto complementario en la base de datos."""
        ...

    @abstractmethod
    def get_complementary_by_id(self, complementary_id: int) -> tuple[int, int] | None:
        """Obtiene la información de un complementario (id, valor)."""
        ...

    @abstractmethod
    def assign_complementary_to_enrollment(
        self,
        matricula_id: int,
        complementary_id: int,
        valor_completo: int,
        descuento: int,
    ) -> int:
        """
        Asigna un complementario a una matrícula existente (crea DetalleMatricula).
        Retorna el ID del DetalleMatricula creado.
        """
        ...

    @abstractmethod
    def increase_enrollment_total_value(self, matricula_id: int, amount: int) -> None:
        """Incrementa el valor total de la matrícula por la suma de un nuevo complementario."""
        ...

    @abstractmethod
    def update_enrollment_details(
        self,
        matricula_id: int,
        nuevo_valor_total: int,
        nuevo_base: int,
        comp_updates: list[tuple[int, int, int, int]],
    ) -> None:
        """Actualiza los detalles de la matrícula y complementarios."""
        ...

    # === Estudiantes ===

    @abstractmethod
    def find_or_create_student(
        self,
        documento: str,
        nombre: str,
        grado_id: int,
        acudiente_id: int,
    ) -> int:
        """Busca un estudiante por documento; si no existe lo crea. Retorna el ID."""
        ...

    @abstractmethod
    def get_payments_count(self, matricula_id: int) -> int:
        """Retorna la cantidad de pagos registrados para una matrícula."""
        ...

    @abstractmethod
    def get_total_paid(self, matricula_id: int) -> int:
        """Retorna la suma total de pagos registrados para una matrícula."""
        ...

    @abstractmethod
    def get_base_paid_amount(self, matricula_id: int) -> int:
        """Retorna la suma total de pagos realizados a la matrícula base."""
        ...

    @abstractmethod
    def get_payments(self, matricula_id: int) -> list:
        """Retorna la lista de pagos registrados para una matrícula."""
        ...

    @abstractmethod
    def search_students(
        self,
        documento: str | None,
        nombre: str | None,
        query: str | None = None,
    ) -> list[tuple]:
        """Busca estudiantes por coincidencia parcial en documento, nombre o consulta general."""
        ...

    @abstractmethod
    def search_active_students(
        self, query: str | None, grado_id: int | None, limit: int, offset: int
    ) -> list[StudentGeneralInfo]:
        """Busca estudiantes activos con filtros opcionales de query y grado, con paginación."""
        ...

    @abstractmethod
    def get_students_bulk(self, student_ids: list[int]) -> list[StudentGeneralInfo]:
        """Obtiene información resumida de un lote de IDs de estudiantes."""
        ...

    @abstractmethod
    def get_all_grades(self) -> list[GradeInfo]:
        """Obtiene la lista de todos los grados académicos."""
        ...

    @abstractmethod
    def get_all_periods(self) -> list[Periodo]:
        """Obtiene la lista de todos los periodos académicos."""
        ...

    @abstractmethod
    def get_student_entity_by_id(self, student_id: int) -> Estudiante | None:
        """Obtiene el objeto/entidad Estudiante crudo por su ID."""
        ...

    @abstractmethod
    def get_student_entities_by_grade(self, grado_id: int) -> list[Estudiante]:
        """Obtiene la lista de entidades Estudiante crudas por grado ID."""
        ...

    @abstractmethod
    def get_all_complementaries_by_year(self, year: int) -> list[Complementario]:
        """Obtiene todos los conceptos complementarios activos por año."""

    # === Nuevas Consultas y Acciones ===

    @abstractmethod
    def get_grade_by_name(self, name: str) -> int | None:
        """Busca un grado por su nombre (insensible a mayúsculas). Retorna su ID."""
        ...

    @abstractmethod
    def get_acudiente_by_name(self, name: str) -> int | None:
        """Busca un acudiente por su nombre. Retorna su ID."""
        ...

    @abstractmethod
    def create_acudiente(
        self, nombre: str, parentesco: str, telefono: str, correo: str
    ) -> int:
        """Crea un acudiente y retorna su ID."""
        ...

    @abstractmethod
    def get_payments_by_matricula(self, matricula_id: int) -> list[Pago]:
        """Retorna todos los pagos (Pago) de una matrícula."""
        ...

    @abstractmethod
    def get_payment_by_id(self, pago_id: int) -> tuple | None:
        """Retorna un pago por su ID como tupla."""
        ...

    @abstractmethod
    def get_payment_details(self, pago_id: int) -> list[tuple[str, int | None, int]]:
        """Retorna los detalles de un pago como lista de (concepto, complementario_id, monto_aplicado)."""
        ...

    @abstractmethod
    def get_payment_receipt_data(self, pago_id: int) -> tuple | None:
        """Retorna los datos crudos del recibo (Pago, Matricula, Estudiante, Grado, Acudiente) como tupla."""
        ...

    @abstractmethod
    def get_detalle_matricula(self, detalle_id: int) -> tuple | None:
        """Obtiene un detalle de matrícula por su ID."""
        ...

    @abstractmethod
    def delete_detalle_matricula(self, detalle_id: int) -> None:
        """Elimina un detalle de matrícula de la base de datos."""
        ...

    @abstractmethod
    def decrease_enrollment_total_value(self, matricula_id: int, amount: int) -> None:
        """Disminuye el valor total de una matrícula."""
        ...

    @abstractmethod
    def get_all_complementaries(
        self, year: int | None = None
    ) -> list[ComplementaryConcept]:
        """Obtiene todos los conceptos complementarios registrados, opcionalmente filtrados por año."""
        ...
