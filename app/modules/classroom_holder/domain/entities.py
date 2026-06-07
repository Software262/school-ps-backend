from dataclasses import dataclass
from datetime import UTC, datetime

from app.modules.classroom_holder.domain.enums import TipoIncidencia


@dataclass
class EstudianteResumen:
    id: int
    nombre: str
    grado_nombre: str


class IncidenciaDomain:
    def __init__(
        self,
        id: int | None,
        estudiante_id: int,
        docente_id: int,
        tipo_incidencia: TipoIncidencia,
        descripcion: str,
        fecha: datetime,
        esta_abierta: bool = True,
        fecha_cierre: datetime | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        self.id = id
        self.estudiante_id = estudiante_id
        self.docente_id = docente_id
        self.tipo_incidencia = tipo_incidencia
        self.descripcion = descripcion
        self.fecha = fecha
        self.esta_abierta = esta_abierta
        self.fecha_cierre = fecha_cierre
        self.created_at = created_at or datetime.now(UTC)
        self.updated_at = updated_at or datetime.now(UTC)

    def cerrar(self):
        """Regla de dominio para el cierre formal de una incidencia."""
        self.esta_abierta = False
        self.fecha_cierre = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)
