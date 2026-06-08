from sqlmodel import select

from app.modules.enrollment.infrastructure.models import Docente, Estudiante, Grado
from app.modules.peace_safe.infrastructure.repository import PeaceSafeRepository
from app.modules.peace_safe.schemas.response import (
    DocenteInfo,
    EstudianteInfo,
    ModuloStatus,
    StatusResponse,
)


STUDENT_MODULES: list[tuple[str, str, str]] = [
    ("enrollment", "Matrícula", "check_matricula"),
    ("tuition", "Pensión", "check_pension"),
    ("cafeteria", "Cafetería", "check_cafeteria"),
    ("pupitre", "Pupitre", "check_pupitre"),
    ("observador", "Observaciones del salón", "check_observador"),
    ("chess", "Ajedrez", "check_chess"),
    ("band", "Banda Musical", "check_band"),
    ("sports", "Deportes", "check_sports"),
    ("training_schools", "Esc. Formación", "check_training_schools"),
    ("tests", "Pruebas", "check_tests"),
]

TEACHER_MODULES: list[tuple[str, str, str]] = [
    ("rectoria", "Rectoría", "check_rectoria"),
]


class PeaceSafeService:
    def __init__(self, repo: PeaceSafeRepository):
        self.repo = repo

    def get_student_status(self, estudiante_id: int) -> StatusResponse | None:
        estudiante = self.repo.session.get(Estudiante, estudiante_id)
        if not estudiante:
            return None

        grado_nombre = None
        if estudiante.grado_id:
            stmt = select(Grado.nombre).where(Grado.id == estudiante.grado_id)
            result = self.repo.session.exec(stmt).first()
            if result:
                grado_nombre = result

        periodo = self.repo.get_active_period()
        periodo_id = periodo.id if periodo else 0

        entidad = EstudianteInfo(estudiante, grado_nombre)

        modulos: list[dict] = []
        for clave, nombre, method_name in STUDENT_MODULES:
            method = getattr(self.repo, method_name)
            try:
                if clave in ("cafeteria", "enrollment"):
                    result = method(estudiante_id, periodo_id)
                else:
                    result = method(estudiante_id)
                estado = "ok" if result["ok"] else "error"
                detalle = result["detalle"]
            except Exception as e:
                self.repo.session.rollback()
                estado = "error"
                detalle = f"Error al consultar: {e}"
            modulos.append(ModuloStatus(clave, nombre, estado, detalle).to_dict())

        return StatusResponse(entidad.to_dict(), modulos)

    def get_teacher_status(self, docente_id: int) -> StatusResponse | None:
        docente = self.repo.session.get(Docente, docente_id)
        if not docente:
            return None

        periodo = self.repo.get_active_period()
        periodo_id = periodo.id if periodo else 0

        entidad = DocenteInfo(docente)

        modulos: list[dict] = []
        for clave, nombre, method_name in TEACHER_MODULES:
            method = getattr(self.repo, method_name)
            try:
                result = method(docente_id, periodo_id)
                estado = "ok" if result["ok"] else "error"
                detalle = result["detalle"]
            except Exception as e:
                estado = "error"
                detalle = f"Error al consultar: {e}"
            modulos.append(ModuloStatus(clave, nombre, estado, detalle).to_dict())

        return StatusResponse(entidad.to_dict(), modulos)

    def generate_student_pazysalvo(
        self, estudiante_id: int, usuario_id: int
    ) -> dict | None:
        status = self.get_student_status(estudiante_id)
        if not status:
            return None

        if not status.paz_y_salvo:
            raise ValueError("El estudiante no está a paz y salvo en todos los módulos")

        periodo = self.repo.get_active_period()
        periodo_id = periodo.id if periodo else 0

        detalles = [
            {
                "modulo": m["clave"],
                "nombre": m["nombre"],
                "estado": m["estado"],
                "detalle": m["detalle"],
            }
            for m in status.modulos
        ]

        record = self.repo.save_pazysalvo(
            entidad_tipo="estudiante",
            entidad_id=estudiante_id,
            periodo_id=periodo_id,
            usuario_id=usuario_id,
            estado_final="paz_y_salvo",
            detalles=detalles,
        )

        return {
            "id": record.id,
            "codigo": record.codigo_certificado,
            "estado_final": record.estado_final,
            "fecha": (
                record.fecha_generacion.isoformat() if record.fecha_generacion else ""
            ),
            "entidad": {
                "nombre": status.entidad["nombre"],
                "documento": status.entidad["documento"],
                "grado": status.entidad.get("grado"),
            },
            "periodo": {
                "id": periodo_id,
                "nombre": f"Periodo {periodo_id}",
            },
            "detalles": detalles,
        }

    def generate_teacher_pazysalvo(
        self, docente_id: int, usuario_id: int
    ) -> dict | None:
        status = self.get_teacher_status(docente_id)
        if not status:
            return None

        if not status.paz_y_salvo:
            raise ValueError("El docente no está a paz y salvo en rectoría")

        periodo = self.repo.get_active_period()
        periodo_id = periodo.id if periodo else 0
        periodo_nombre = (
            periodo.periodo_electivo.isoformat()
            if periodo and periodo.periodo_electivo
            else f"Periodo {periodo_id}"
        )

        detalles = [
            {
                "modulo": m["clave"],
                "nombre": m["nombre"],
                "estado": m["estado"],
                "detalle": m["detalle"],
            }
            for m in status.modulos
        ]

        record = self.repo.save_pazysalvo(
            entidad_tipo="docente",
            entidad_id=docente_id,
            periodo_id=periodo_id,
            usuario_id=usuario_id,
            estado_final="paz_y_salvo",
            detalles=detalles,
        )

        return {
            "id": record.id,
            "codigo": record.codigo_certificado,
            "estado_final": record.estado_final,
            "fecha": (
                record.fecha_generacion.isoformat() if record.fecha_generacion else ""
            ),
            "entidad": {
                "nombre": status.entidad["nombre"],
                "documento": status.entidad["documento"],
            },
            "periodo": {
                "id": periodo_id,
                "nombre": periodo_nombre,
            },
            "detalles": detalles,
        }
