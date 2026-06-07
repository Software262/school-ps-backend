from sqlmodel import Session

from app.modules.enrollment.infrastructure.models import Estudiante
from app.modules.inventory.application.contracts import InventoryEnrollmentService
from app.modules.inventory.domain.entities import StudentEntity


class InventoryEnrollmentAdapter(InventoryEnrollmentService):
    """Adapter that implements InventoryEnrollmentService using enrollment's DB models."""

    def __init__(self, session: Session):
        self.session = session

    def get_student_by_id(self, student_id: int) -> StudentEntity | None:
        student = self.session.get(Estudiante, student_id)
        if not student:
            return None
        return StudentEntity(
            id=student.id or 0,
            nombre=student.nombre,
            activo=student.activo,
        )
