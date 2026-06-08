from sqlmodel import Session

from app.modules.peace_safe.domain.service import PeaceSafeService
from app.modules.peace_safe.infrastructure.repository import PeaceSafeRepository


class GenerateStudentPazYSalvo:
    def __init__(self, session: Session):
        self.service = PeaceSafeService(PeaceSafeRepository(session))

    async def execute(self, estudiante_id: int, usuario_id: int) -> dict | None:
        return self.service.generate_student_pazysalvo(estudiante_id, usuario_id)


class GenerateTeacherPazYSalvo:
    def __init__(self, session: Session):
        self.service = PeaceSafeService(PeaceSafeRepository(session))

    async def execute(self, docente_id: int, usuario_id: int) -> dict | None:
        return self.service.generate_teacher_pazysalvo(docente_id, usuario_id)


class GetPazYSalvoDetail:
    def __init__(self, session: Session):
        self.repo = PeaceSafeRepository(session)

    async def execute(self, pazysalvo_id: int) -> dict | None:
        record = self.repo.get_pazysalvo(pazysalvo_id)
        if not record:
            return None

        detalles = self.repo.get_detalles(pazysalvo_id)

        if record.entidad_tipo == "estudiante":
            from app.modules.enrollment.infrastructure.models import Estudiante

            estudiante = self.repo.session.get(Estudiante, record.entidad_id)
            entidad_info = (
                {
                    "id": estudiante.id,
                    "nombre": estudiante.nombre,
                    "documento": estudiante.documento,
                }
                if estudiante
                else {}
            )
        else:
            from app.modules.enrollment.infrastructure.models import Docente

            docente = self.repo.session.get(Docente, record.entidad_id)
            entidad_info = (
                {
                    "id": docente.id,
                    "nombre": docente.nombre,
                    "documento": docente.documento,
                }
                if docente
                else {}
            )

        return {
            "id": record.id,
            "codigo": record.codigo_certificado,
            "entidad_tipo": record.entidad_tipo,
            "estado_final": record.estado_final,
            "fecha_generacion": (
                record.fecha_generacion.isoformat() if record.fecha_generacion else ""
            ),
            "entidad": entidad_info,
            "detalles": [
                {
                    "modulo": d.modulo,
                    "nombre_modulo": d.nombre_modulo,
                    "estado": d.estado,
                    "detalle": d.detalle,
                }
                for d in (detalles or [])
            ],
        }
