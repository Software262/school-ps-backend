from sqlmodel import col, select

from app.core.db import SessionDep
from app.modules.enrollment.infrastructure.models import Estudiante
from app.modules.inventory.application.contracts import InventoryEnrollmentService
from app.modules.inventory.domain.entities import StudentEntity


class InventoryEnrollmentAdapter(InventoryEnrollmentService):
    """Adapter that implements InventoryEnrollmentService using enrollment's DB models."""

    def __init__(self, session: SessionDep):
        self.session = session

    def get_student_by_id(self, student_id: int) -> StudentEntity | None:
        student = self.session.exec(
            select(Estudiante).where(
                Estudiante.id == student_id, col(Estudiante.activo).is_(True)
            )
        ).first()

        if not student:
            return None
        return StudentEntity(
            id=student.id or 0,
            nombre=student.nombre,
            activo=student.activo,
        )
