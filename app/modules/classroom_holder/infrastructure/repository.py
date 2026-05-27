from typing import List, Optional
from sqlmodel import Session, select
from app.modules.classroom_holder.domain.entities import IncidenciaDomain
from app.modules.classroom_holder.domain.enums import TipoIncidencia
from app.modules.classroom_holder.domain.repositories import IncidenciaRepositoryInterface
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
            updated_at=model.updated_at
        )

    def save(self, domain: IncidenciaDomain) -> IncidenciaDomain:
        if domain.id is not None:
            model = self.session.get(Observador, domain.id)
            if model:
                model.esta_abierta = domain.esta_abierta
                model.fecha_cierre = domain.fecha_cierre
                model.updated_at = domain.updated_at
                model.descripcion = domain.descripcion
        else:
            model = Observador(
                estudiante_id=domain.estudiante_id,
                docente_id=domain.docente_id,
                tipo_incidencia=domain.tipo_incidencia.value,
                descripcion=domain.descripcion,
                fecha=domain.fecha,
                esta_abierta=domain.esta_abierta,
                fecha_cierre=domain.fecha_cierre,
                created_at=domain.created_at,
                updated_at=domain.updated_at
            )
        
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_domain(model)

    def find_by_id(self, incidencia_id: int) -> Optional[IncidenciaDomain]:
        model = self.session.get(Observador, incidencia_id)
        if not model:
            return None
        return self._to_domain(model)

    def find_by_student(self, estudiante_id: int) -> List[IncidenciaDomain]:
        statement = select(Observador).where(Observador.estudiante_id == estudiante_id)
        results = self.session.exec(statement).all()
        return [self._to_domain(row) for row in results]

    def has_open_incidents(self, estudiante_id: int) -> bool:
        statement = select(Observador).where(
            Observador.estudiante_id == estudiante_id,
            Observador.esta_abierta == True
        )
        result = self.session.exec(statement).first()
        return result is not None