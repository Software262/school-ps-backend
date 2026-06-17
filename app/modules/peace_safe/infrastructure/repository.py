from datetime import datetime, timezone

from sqlmodel import col, select

from app.core.db import SessionDep
from app.modules.cafeteria.infrastructure.models import Cafeteria
from app.modules.classroom.infrastructure.models import DetallePupitre
from app.modules.classroom_holder.infrastructure.models import Observador
from app.modules.enrollment.infrastructure.models import (
    DetalleMatricula,
    Docente,
    Estudiante,
    Grado,
    Matricula,
    Periodo,
)
from app.modules.inventory.infrastructure.models import (
    Inventario,
    Novedad,
    Prestamo,
    TipoInventario,
)
from app.modules.peace_safe.domain.repositories import (
    PeaceSafeRepository as PeaceSafeRepositoryInterface,
)
from app.modules.peace_safe.infrastructure.models import (
    DetallePazYSalvo,
    PazYSalvo,
)
from app.modules.principal.infrastructure.models import RectoriaEstado
from app.modules.tests.infrastructure.models import DetallePrueba
from app.modules.training_schools.infrastructure.models import DetalleEscuelaFormacion
from app.modules.tuition.infrastructure.models import Pension


class PeaceSafeRepository(PeaceSafeRepositoryInterface):
    def __init__(self, session: SessionDep):
        self.session = session

    # ── Búsqueda ──────────────────────────────────────────────────────────

    def search_students(self, query: str) -> list[Estudiante]:
        pattern = f"%{query}%"
        return list(
            self.session.exec(
                select(Estudiante).where(
                    (col(Estudiante.nombre).ilike(pattern))
                    | (col(Estudiante.documento).ilike(pattern))
                )
            ).all()
        )

    def search_teachers(self, query: str) -> list[Docente]:
        pattern = f"%{query}%"
        return list(
            self.session.exec(
                select(Docente).where(
                    (col(Docente.nombre).ilike(pattern))
                    | (col(Docente.documento).ilike(pattern))
                )
            ).all()
        )

    def get_active_period(self) -> Periodo | None:
        return self.session.exec(select(Periodo).where(col(Periodo.estado))).first()

    def get_student(self, estudiante_id: int) -> Estudiante | None:
        return self.session.get(Estudiante, estudiante_id)

    def get_grade_name(self, grado_id: int) -> str | None:
        grado = self.session.get(Grado, grado_id)
        return grado.nombre if grado else None

    def get_teacher(self, docente_id: int) -> Docente | None:
        return self.session.get(Docente, docente_id)

    # ── Datos de módulos (solo acceso a datos) ──────────────────────────

    def get_matricula(self, estudiante_id: int, periodo_id: int) -> Matricula | None:
        return self.session.exec(
            select(Matricula).where(
                Matricula.estudiante_id == estudiante_id,
                Matricula.periodo_id == periodo_id,
            )
        ).first()

    def get_matricula_detalles(self, matricula_id: int) -> list[DetalleMatricula]:
        return list(
            self.session.exec(
                select(DetalleMatricula).where(
                    DetalleMatricula.matricula_id == matricula_id,
                    DetalleMatricula.valor_pendiente > 0,
                )
            ).all()
        )

    def get_pension(self, estudiante_id: int) -> Pension | None:
        return self.session.exec(
            select(Pension).where(Pension.estudiante_id == estudiante_id)
        ).first()

    def get_cafeteria(self, estudiante_id: int, periodo_id: int) -> Cafeteria | None:
        return self.session.exec(
            select(Cafeteria).where(
                Cafeteria.estudiante_id == estudiante_id,
                Cafeteria.periodo_id == periodo_id,
            )
        ).first()

    def get_pupitre_by_student(self, estudiante_id: int) -> DetallePupitre | None:
        return self.session.exec(
            select(DetallePupitre).where(DetallePupitre.estudiante_id == estudiante_id)
        ).first()

    def get_observaciones(self, estudiante_id: int) -> list[Observador]:
        return list(
            self.session.exec(
                select(Observador).where(Observador.estudiante_id == estudiante_id)
            ).all()
        )

    def get_loans_by_type(
        self, estudiante_id: int, tipo_nombre: str
    ) -> tuple[list[Prestamo], list[Novedad]]:
        tipo = self.session.exec(
            select(TipoInventario).where(col(TipoInventario.nombre).ilike(tipo_nombre))
        ).first()

        if not tipo:
            return [], []

        prestamos = list(
            self.session.exec(
                select(Prestamo)
                .join(Inventario)
                .where(
                    Prestamo.estudiante_id == estudiante_id,
                    Inventario.tipo_inventario_id == tipo.id,
                )
            ).all()
        )

        ids = [p.id for p in prestamos]
        if not ids:
            return prestamos, []

        novedades = list(
            self.session.exec(
                select(Novedad).where(
                    col(Novedad.prestamo_id).in_(ids),
                    not col(Novedad.resuelta),
                )
            ).all()
        )
        return prestamos, novedades

    def get_training_school_details(
        self, estudiante_id: int
    ) -> list[DetalleEscuelaFormacion]:
        return list(
            self.session.exec(
                select(DetalleEscuelaFormacion).where(
                    DetalleEscuelaFormacion.estudiante_id == estudiante_id,
                    col(DetalleEscuelaFormacion.activo),
                )
            ).all()
        )

    def get_test_details(self, estudiante_id: int) -> list[DetallePrueba]:
        return list(
            self.session.exec(
                select(DetallePrueba).where(
                    DetallePrueba.estudiante_id == estudiante_id,
                    DetallePrueba.estado == "pendiente",
                )
            ).all()
        )

    def get_rectoria_status(self, docente_id: int) -> RectoriaEstado | None:
        return self.session.exec(
            select(RectoriaEstado).where(
                RectoriaEstado.docente_id == docente_id,
            )
        ).first()

    # ── Generación de paz y salvo ──────────────────────────────────────

    def generate_codigo(self) -> str:
        now = datetime.now(timezone.utc)
        ts = now.strftime("%Y%m%d%H%M%S%f")[:18]
        return f"PS-{ts}"

    def save_pazysalvo(
        self,
        entidad_tipo: str,
        entidad_id: int,
        periodo_id: int,
        usuario_id: int,
        estado_final: str,
        detalles: list[dict],
    ) -> PazYSalvo:
        codigo = self.generate_codigo()

        record = PazYSalvo(
            entidad_tipo=entidad_tipo,
            entidad_id=entidad_id,
            periodo_id=periodo_id,
            usuario_genera_id=usuario_id,
            estado_final=estado_final,
            codigo_certificado=codigo,
            fecha_generacion=datetime.now(timezone.utc),
            observacion=None,
        )
        self.session.add(record)
        self.session.flush()

        assert record.id is not None
        for d in detalles:
            detalle = DetallePazYSalvo(
                paz_y_salvo_id=record.id,
                modulo=d["modulo"],
                nombre_modulo=d["nombre"],
                estado=d["estado"],
                detalle=d["detalle"],
            )
            self.session.add(detalle)

        self.session.commit()
        self.session.refresh(record)

        return record

    def get_pazysalvo(self, pazysalvo_id: int) -> PazYSalvo | None:
        return self.session.get(PazYSalvo, pazysalvo_id)

    def get_detalles(self, pazysalvo_id: int) -> list[DetallePazYSalvo]:
        return list(
            self.session.exec(
                select(DetallePazYSalvo).where(
                    DetallePazYSalvo.paz_y_salvo_id == pazysalvo_id
                )
            ).all()
        )
