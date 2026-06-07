from sqlmodel import Session, col, select

from app.modules.classroom_holder.domain.entities import IncidenciaDomain
from app.modules.classroom_holder.domain.enums import TipoIncidencia
from app.modules.classroom_holder.domain.repositories import (
    IncidenciaRepositoryInterface,
)
from app.modules.classroom_holder.infrastructure.models import Observador


class IncidenciaRepository(IncidenciaRepositoryInterface):
    def __init__(self, session: Session):
        self.session = session

    def _to_domain(self, model: Observador) -> IncidenciaDomain:
        return IncidenciaDomain(
            id=model.id,
            estudiante_id=model.estudiante_id,
            docente_id=model.docente_id,
            tipo_incidencia=TipoIncidencia(model.tipo_incidencia),
            descripcion=model.descripcion,
            fecha=model.fecha,
            esta_abierta=model.esta_abierta,
            fecha_cierre=model.fecha_cierre,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def save(self, incidencia: IncidenciaDomain) -> IncidenciaDomain:
        if incidencia.id is not None:
            model = self.session.get(Observador, incidencia.id)
            if model:
                model.esta_abierta = incidencia.esta_abierta
                model.fecha_cierre = incidencia.fecha_cierre
                model.updated_at = incidencia.updated_at
                model.descripcion = incidencia.descripcion
                self.session.add(model)
                self.session.commit()
                self.session.refresh(model)
                return self._to_domain(model)

        model = Observador(
            estudiante_id=incidencia.estudiante_id,
            docente_id=incidencia.docente_id,
            tipo_incidencia=incidencia.tipo_incidencia.value,
            descripcion=incidencia.descripcion,
            fecha=incidencia.fecha,
            esta_abierta=incidencia.esta_abierta,
            fecha_cierre=incidencia.fecha_cierre,
            created_at=incidencia.created_at,
            updated_at=incidencia.updated_at,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_domain(model)

    def find_by_id(self, incidencia_id: int) -> IncidenciaDomain | None:
        model = self.session.get(Observador, incidencia_id)
        if not model:
            return None
        return self._to_domain(model)

    def find_by_student(self, estudiante_id: int) -> list[IncidenciaDomain]:
        statement = select(Observador).where(Observador.estudiante_id == estudiante_id)
        results = self.session.exec(statement).all()
        return [self._to_domain(row) for row in results]

    def has_open_incidents(self, estudiante_id: int) -> bool:
        statement = select(Observador).where(
            Observador.estudiante_id == estudiante_id, col(Observador.esta_abierta)
        )
        result = self.session.exec(statement).first()
        return result is not None
