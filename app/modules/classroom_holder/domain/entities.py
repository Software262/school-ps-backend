from datetime import datetime
from typing import Optional
from app.modules.classroom_holder.domain.enums import TipoIncidencia

class IncidenciaDomain:
    def __init__(
        self,
        id: Optional[int],
        estudiante_id: int,
        docente_id: int,
        tipo_incidencia: TipoIncidencia,
        descripcion: str,
        fecha: datetime,
        esta_abierta: bool = True,
        fecha_cierre: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.estudiante_id = estudiante_id
        self.docente_id = docente_id
        self.tipo_incidencia = tipo_incidencia
        self.descripcion = descripcion
        self.fecha = fecha
        self.esta_abierta = esta_abierta
        self.fecha_cierre = fecha_cierre
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def cerrar(self):
        """Regla de dominio para el cierre formal de una incidencia."""
        self.esta_abierta = False
        self.fecha_cierre = datetime.utcnow()
        self.updated_at = datetime.utcnow()