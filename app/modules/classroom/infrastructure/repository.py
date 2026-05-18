from domain.repository import PupitreRepository
from sqlmodel import Session,select
from domain.entity import Pupitre

class PupitreRepositoryImpl(PupitreRepository):
    def __init__(self, db: Session):
        self.db = db

    def obtener_por_estudiante(self, estudiante_id: int):
        pupitre = self.db.exec(select(Pupitre).where(Pupitre.estudiante_id == estudiante_id)).first()
        if pupitre is None:
            raise ValueError(f"Pupitre no encontrado para el estudiante con ID: {estudiante_id}")
        return pupitre

    def guardar_pupitre(self, pupitre: Pupitre) -> Pupitre:
        try:
            self.db.add(pupitre)
            self.db.commit()
            self.db.refresh(pupitre)
            return pupitre
        except Exception as e:
            self.db.rollback()
            raise e

    def obtener_por_grado(self, grado_id: int) -> list[Pupitre]:
        pass