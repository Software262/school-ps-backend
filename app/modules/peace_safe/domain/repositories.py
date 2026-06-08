from abc import ABC, abstractmethod

from app.modules.cafeteria.infrastructure.models import Cafeteria
from app.modules.classroom.infrastructure.models import Pupitre
from app.modules.classroom_holder.infrastructure.models import Observador
from app.modules.enrollment.infrastructure.models import (
    DetalleMatricula,
    Docente,
    Estudiante,
    Matricula,
    Periodo,
)
from app.modules.inventory.infrastructure.models import Novedad, Prestamo
from app.modules.peace_safe.infrastructure.models import DetallePazYSalvo, PazYSalvo
from app.modules.principal.infrastructure.models import RectoriaEstado
from app.modules.tests.infrastructure.models import DetallePrueba
from app.modules.training_schools.infrastructure.models import DetalleEscuelaFormacion
from app.modules.tuition.infrastructure.models import Pension


class PeaceSafeRepository(ABC):

    @abstractmethod
    def search_students(self, query: str) -> list[Estudiante]: ...

    @abstractmethod
    def search_teachers(self, query: str) -> list[Docente]: ...

    @abstractmethod
    def get_active_period(self) -> Periodo | None: ...

    @abstractmethod
    def get_student(self, estudiante_id: int) -> Estudiante | None: ...

    @abstractmethod
    def get_grade_name(self, grado_id: int) -> str | None: ...

    @abstractmethod
    def get_teacher(self, docente_id: int) -> Docente | None: ...

    @abstractmethod
    def get_matricula(self, estudiante_id: int, periodo_id: int) -> Matricula | None: ...

    @abstractmethod
    def get_matricula_detalles(self, matricula_id: int) -> list[DetalleMatricula]: ...

    @abstractmethod
    def get_pension(self, estudiante_id: int) -> Pension | None: ...

    @abstractmethod
    def get_cafeteria(self, estudiante_id: int, periodo_id: int) -> Cafeteria | None: ...

    @abstractmethod
    def get_pupitre_by_student(self, estudiante_id: int) -> Pupitre | None: ...

    @abstractmethod
    def get_observaciones(self, estudiante_id: int) -> list[Observador]: ...

    @abstractmethod
    def get_loans_by_type(
        self, estudiante_id: int, tipo_nombre: str
    ) -> tuple[list[Prestamo], list[Novedad]]: ...

    @abstractmethod
    def get_training_school_details(self, estudiante_id: int) -> list[DetalleEscuelaFormacion]: ...

    @abstractmethod
    def get_test_details(self, estudiante_id: int) -> list[DetallePrueba]: ...

    @abstractmethod
    def get_rectoria_status(self, docente_id: int) -> RectoriaEstado | None: ...

    @abstractmethod
    def save_pazysalvo(
        self,
        entidad_tipo: str,
        entidad_id: int,
        periodo_id: int,
        usuario_id: int,
        estado_final: str,
        detalles: list[dict],
    ) -> PazYSalvo: ...

    @abstractmethod
    def get_pazysalvo(self, pazysalvo_id: int) -> PazYSalvo | None: ...

    @abstractmethod
    def get_detalles(self, pazysalvo_id: int) -> list[DetallePazYSalvo]: ...
