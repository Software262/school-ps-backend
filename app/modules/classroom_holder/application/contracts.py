from abc import ABC, abstractmethod

from app.modules.classroom_holder.domain.entities import EstudianteResumen


class ClassroomEnrollmentService(ABC):
    """Contract for enrollment-owned data that the classroom_holder module needs."""

    @abstractmethod
    def buscar_estudiantes_por_nombre(self, query: str) -> list[EstudianteResumen]:
        pass
