from sqlmodel import select
from app.core.db import SessionDep
from app.modules.classroom.infrastructure.models import Pupitre
from app.modules.classroom.domain.repositories import PupitreRepository

class PupitreRepositoryImpl(PupitreRepository):

    def __init__(self, session: SessionDep):
        self.session = session

    async def obtener_por_estudiante(self, estudiante_id: int) -> Pupitre | None:
        return self.session.exec(
            select(Pupitre).where(Pupitre.estudiante_id == estudiante_id)
        ).one_or_none()

    async def guardar_pupitre(self, pupitre: Pupitre) -> Pupitre:
        self.session.add(pupitre)
        self.session.commit()
        self.session.refresh(pupitre)
        return pupitre

    async def obtener_por_grado(self, grado_id: int) -> list[Pupitre]:
        pass