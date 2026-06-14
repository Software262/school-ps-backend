from sqlmodel import select
from app.core.db import SessionDep
from app.modules.classroom.infrastructure.models import Pupitre
from app.modules.classroom.domain.repositories import PupitreRepository
from sqlmodel import col
from sqlalchemy.exc import SQLAlchemyError


class PupitreRepositoryImpl(PupitreRepository):
    def __init__(self, session: SessionDep):
        self.session = session

    # Se obtiene el pupitre al cual pertenece el estudiante, si no tiene pupitre se retorna None
    async def get_student_desk(self, estudiante_id: int) -> Pupitre | None:
        return self.session.exec(
            select(Pupitre).where(Pupitre.estudiante_id == estudiante_id)
        ).one_or_none()

    # Se actualiza el estado de UN pupitre, se retorna el pupitre actualizado
    async def update_desk_state(self, pupitre: Pupitre) -> Pupitre:
        self.session.commit()
        self.session.refresh(pupitre)
        return pupitre

    # Se obtiene la lista de los pupitres asociados a los estudiantes que pertenecen a un mismo grado, si no se encuentran pupitres se retorna None
    async def list_desks_by_students(self, estudiante_ids: list[int]) -> list[Pupitre]:
        return list(
            self.session.exec(
                select(Pupitre).where(col(Pupitre.estudiante_id).in_(estudiante_ids))
            ).all()
        )

    # Se actualiza el estado de varios pupitres, se retorna la cantidad de pupitres actualizados
    async def bulk_update_desk_states(self, pupitres: list[Pupitre]) -> int:
        try:
            self.session.commit()
            return len(pupitres)
        except SQLAlchemyError:
            self.session.rollback()
            raise

    # Se crea un nuevo pupitre, se retorna el pupitre creado
    async def add_desk(
        self, estudiante_id: int, estado_pupitre: bool, observacion: str | None
    ) -> Pupitre:
        try:
            nuevo_pupitre = Pupitre(
                estudiante_id=estudiante_id,
                estado_pupitre=estado_pupitre,
                observacion=observacion,
            )
            self.session.add(nuevo_pupitre)
            self.session.commit()
            self.session.refresh(nuevo_pupitre)
            return nuevo_pupitre
        except SQLAlchemyError:
            self.session.rollback()
            raise
