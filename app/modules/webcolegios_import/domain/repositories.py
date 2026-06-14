from abc import ABC, abstractmethod
from typing import Sequence

from app.modules.auth.infrastructure.models import ImportacionAutomatica
from app.modules.enrollment.infrastructure.models import (
    Acudiente,
    Docente,
    Estudiante,
    Grado,
)
from app.modules.webcolegios_import.domain.entities import (
    ScrapedStudent,
    ScrapedTeacher,
)

WEBCOLEGIOS_STUDENT_ENTITY = "WEB_ESTUDIANTE"
WEBCOLEGIOS_TEACHER_ENTITY = "WEB_DOCENTE"
WEBCOLEGIOS_SYSTEM_ENTITY = "WEB_SISTEMA"
WEBCOLEGIOS_ENTITY_TYPES = (
    WEBCOLEGIOS_STUDENT_ENTITY,
    WEBCOLEGIOS_TEACHER_ENTITY,
    WEBCOLEGIOS_SYSTEM_ENTITY,
)


class WebcolegiosImportRepository(ABC):
    @abstractmethod
    def clear_staging(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def save_staging_students(self, students: list[ScrapedStudent]) -> None:
        raise NotImplementedError

    @abstractmethod
    def save_staging_teachers(self, teachers: list[ScrapedTeacher]) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_staging_students(self) -> list[ScrapedStudent]:
        raise NotImplementedError

    @abstractmethod
    def get_staging_teachers(self) -> list[ScrapedTeacher]:
        raise NotImplementedError

    @abstractmethod
    def find_student_by_document(self, document: str) -> Estudiante | None:
        raise NotImplementedError

    @abstractmethod
    def find_teacher_by_document(self, document: str) -> Docente | None:
        raise NotImplementedError

    @abstractmethod
    def find_teacher_by_name(self, name: str | None) -> Docente | None:
        raise NotImplementedError

    @abstractmethod
    def find_grade_by_name(self, name: str | None) -> Grado | None:
        raise NotImplementedError

    @abstractmethod
    def get_or_create_grade_by_name(self, grade_name: str | None) -> Grado | None:
        raise NotImplementedError

    @abstractmethod
    def find_guardian(
        self, name: str | None, phone: str | None, email: str | None
    ) -> Acudiente | None:
        raise NotImplementedError

    @abstractmethod
    def get_or_create_default_guardian_na(self) -> Acudiente:
        raise NotImplementedError

    @abstractmethod
    def get_or_create_guardian(
        self, name: str | None, phone: str | None, email: str | None
    ) -> Acudiente:
        raise NotImplementedError

    @abstractmethod
    def is_default_guardian(self, guardian_id: int | None) -> bool:
        raise NotImplementedError

    @abstractmethod
    def update_student_guardian(
        self, student: Estudiante, guardian_id: int
    ) -> Estudiante:
        raise NotImplementedError

    @abstractmethod
    def update_student_grade(self, student: Estudiante, grade_id: int) -> Estudiante:
        raise NotImplementedError

    @abstractmethod
    def create_student(
        self, nombre: str, documento: str, grado_id: int, acudiente_id: int
    ) -> Estudiante:
        raise NotImplementedError

    @abstractmethod
    def create_teacher(self, nombre: str, documento: str, asignatura: str) -> Docente:
        raise NotImplementedError

    @abstractmethod
    def register_import_result(
        self,
        tipo_entidad: str,
        documento_identidad: str,
        datos: str,
        estado: str,
        observacion: str,
    ) -> ImportacionAutomatica:
        raise NotImplementedError

    @abstractmethod
    def update_import_result_status(
        self,
        record: ImportacionAutomatica,
        estado: str,
        observacion: str,
    ) -> ImportacionAutomatica:
        raise NotImplementedError

    @abstractmethod
    def get_history(self, limit: int) -> Sequence[ImportacionAutomatica]:
        raise NotImplementedError

    @abstractmethod
    def get_errors(self, limit: int) -> Sequence[ImportacionAutomatica]:
        raise NotImplementedError

    @abstractmethod
    def get_pending_student_imports(self) -> Sequence[ImportacionAutomatica]:
        raise NotImplementedError

    @abstractmethod
    def clear_history(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def clear_errors(self) -> int:
        raise NotImplementedError
