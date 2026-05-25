from sqlmodel import select
from app.core.db import SessionDep
from app.modules.classroom.infrastructure.models import Pupitre
from app.modules.enrollment.infrastructure.models import Estudiante
from app.modules.classroom.domain.repositories import PupitreRepository

class PupitreRepositoryImpl(PupitreRepository):

    def __init__(self, session: SessionDep):
        self.session = session

#Se obtiene el pupitre por el id del estudiante, si no existe retorna None
    async def obtener_por_estudiante(self, estudiante_id: int) -> Pupitre | None:
        return self.session.exec(
            select(Pupitre).where(Pupitre.estudiante_id == estudiante_id)
        ).one_or_none()

#Se guarda el estado del pupitre, si el pupitre no existe, retornamos None 
    async def guardar_pupitre(self, pupitre: Pupitre) -> Pupitre:
        self.session.add(pupitre)
        self.session.commit()
        self.session.refresh(pupitre)
        return pupitre
    
#Se obtienen todos los pupitres de un grado, si no existen retorna None
    async def obtener_por_grado(self, grado_id: int) -> list[Pupitre]:
        return list(self.session.exec(
        select(Pupitre)
        .join(Estudiante)
        .where(Estudiante.grado_id == grado_id)
    ).all())

#Se guardan una lista de pupitres, retornamos la lista de pupitres guardados
    async def guardar_muchos_pupitres(self, pupitres: list[Pupitre]) -> int:
        try:
            for pupitre in pupitres:
                self.session.add(pupitre)
            self.session.commit()
            return len(pupitres)
        except Exception:
            self.session.rollback()
            raise
   