from sqlmodel import select
from app.core.db import SessionDep
from app.modules.enrollment.infrastructure.models import Complementario
from app.modules.tests.infrastructure.models import DetallePrueba


class DeleteTestComplementary:
    """Elimina un complementario de tipo prueba y sus asignaciones asociadas."""

    def __init__(self, session: SessionDep):
        self.session = session

    def execute(self, comp_id: int):
        comp = self.session.get(Complementario, comp_id)
        if not comp:
            raise ValueError("Prueba no encontrada")

        # Eliminar primero las asignaciones relacionadas en DetallePrueba
        detalles = self.session.exec(
            select(DetallePrueba).where(DetallePrueba.complementario_id == comp_id)
        ).all()
        for d in detalles:
            self.session.delete(d)

        self.session.delete(comp)
        self.session.commit()
        return True
