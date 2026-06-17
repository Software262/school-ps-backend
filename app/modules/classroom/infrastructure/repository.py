from sqlmodel import select, col
from sqlalchemy.exc import SQLAlchemyError

from app.core.db import SessionDep
from app.modules.classroom.infrastructure.models import DetallePupitre
from app.modules.classroom.domain.repositories import PupitreRepository
from app.modules.enrollment.infrastructure.models import Estudiante


class PupitreRepositoryImpl(PupitreRepository):
    def __init__(self, session: SessionDep):
        self.session = session

    # Se obtiene el pupitre de un estudiante para un complementario específico (año vigente)
    async def get_student_desk(
        self, estudiante_id: int, complementario_id: int
    ) -> DetallePupitre | None:
        return self.session.exec(
            select(DetallePupitre).where(
                DetallePupitre.estudiante_id == estudiante_id,
                DetallePupitre.complementario_id == complementario_id,
            )
        ).one_or_none()

    # Se actualiza UN pupitre (confirmación de pago individual), se retorna el pupitre actualizado
    async def update_desk(self, pupitre: DetallePupitre) -> DetallePupitre:
        try:
            self.session.add(pupitre)
            self.session.commit()
            self.session.refresh(pupitre)
            return pupitre
        except SQLAlchemyError:
            self.session.rollback()
            raise

    # Se obtiene la lista de pupitres asociados a un grupo de estudiantes (ej. por curso)
    async def list_desks_by_students(
        self, estudiante_ids: list[int]
    ) -> list[DetallePupitre]:
        return list(
            self.session.exec(
                select(DetallePupitre).where(
                    col(DetallePupitre.estudiante_id).in_(estudiante_ids)
                )
            ).all()
        )

    # Se obtiene la lista de pupitres de todos los estudiantes de un grado
    async def list_desks_by_grado_id(self, grado_id: int) -> list[DetallePupitre]:
        return list(
            self.session.exec(
                select(DetallePupitre)
                .join(
                    Estudiante, col(DetallePupitre.estudiante_id) == col(Estudiante.id)
                )
                .where(col(Estudiante.grado_id) == grado_id)
            ).all()
        )

    # Se actualiza el estado de varios pupitres, se retorna la cantidad de pupitres actualizados
    async def bulk_update_desk_states(self, pupitres: list[DetallePupitre]) -> int:
        try:
            for pupitre in pupitres:
                self.session.add(pupitre)
            self.session.commit()
            return len(pupitres)
        except SQLAlchemyError:
            self.session.rollback()
            raise
