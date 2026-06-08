from datetime import datetime, timezone

from sqlmodel import Session, col, select, text

from app.modules.classroom.infrastructure.models import Pupitre
from app.modules.enrollment.infrastructure.models import (
    DetalleMatricula,
    Estudiante,
    Periodo,
    Docente,
)
from app.modules.inventory.infrastructure.models import (
    Inventario,
    Novedad,
    Prestamo,
    TipoInventario,
)
from app.modules.peace_safe.infrastructure.models import (
    DetallePazYSalvo,
    PazYSalvo,
)
from app.modules.principal.infrastructure.models import RectoriaEstado


class PeaceSafeRepository:
    def __init__(self, session: Session):
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
        return self.session.exec(
            select(Periodo).where(Periodo.estado == True)  # noqa: E712
        ).first()

    # ── Estado de módulos para estudiante ──────────────────────────────

    def check_matricula(self, estudiante_id: int, periodo_id: int) -> dict:
        row = self.session.execute(
            text(
                "SELECT id, estado_matricula FROM matricula "
                "WHERE estudiante_id = :eid AND periodo_id = :pid"
            ),
            {"eid": estudiante_id, "pid": periodo_id},
        ).first()
        if not row:
            return {"ok": True, "detalle": "Estudiante matriculado"}

        # estado_matricula is boolean in DB: true = pagado, false = pendiente
        if not row.estado_matricula:
            return {"ok": False, "detalle": "Matrícula pendiente de pago"}

        detalles = self.session.exec(
            select(DetalleMatricula).where(
                DetalleMatricula.matricula_id == row.id,
                DetalleMatricula.valor_pendiente > 0,
            )
        ).all()
        if detalles:
            total = sum(d.valor_pendiente for d in detalles)
            return {"ok": False, "detalle": f"Pendiente de pago: ${total:,}"}

        return {"ok": True, "detalle": "Matrícula pagada"}

    def check_pension(self, estudiante_id: int) -> dict:
        row = self.session.execute(
            text("SELECT id, estado_pension FROM pension WHERE estudiante_id = :eid"),
            {"eid": estudiante_id},
        ).first()
        if not row:
            return {"ok": True, "detalle": "Sin pensión registrada"}

        if not row.estado_pension:
            return {"ok": False, "detalle": "Pensión con estado pendiente"}
        return {"ok": True, "detalle": "Pensión al día"}

    def check_cafeteria(self, estudiante_id: int, periodo_id: int) -> dict:
        row = self.session.execute(
            text(
                "SELECT id, estado_cafeteria FROM cafeteria "
                "WHERE estudiante_id = :eid AND periodo_id = :pid"
            ),
            {"eid": estudiante_id, "pid": periodo_id},
        ).first()
        if row and not row.estado_cafeteria:
            return {"ok": False, "detalle": "Deuda en cafetería"}
        return {"ok": True, "detalle": "Sin deudas en cafetería"}

    def check_pupitre(self, estudiante_id: int) -> dict:
        pupitre = self.session.exec(
            select(Pupitre).where(Pupitre.estudiante_id == estudiante_id)
        ).first()
        if pupitre and not pupitre.estado_pupitre:
            obs = pupitre.observacion or "Sin detalles"
            return {"ok": False, "detalle": f"Pupitre no devuelto: {obs}"}
        return {"ok": True, "detalle": "Pupitre en orden"}

    def check_observador(self, estudiante_id: int) -> dict:
        rows = self.session.execute(
            text(
                "SELECT id, tipo_incidencia FROM observador WHERE estudiante_id = :eid"
            ),
            {"eid": estudiante_id},
        ).all()
        if rows:
            tipos = list(set(r.tipo_incidencia for r in rows))
            return {
                "ok": False,
                "detalle": f"Incidencias registradas: {', '.join(tipos)} ({len(rows)})",
            }
        return {"ok": True, "detalle": "Sin incidencias registradas"}

    def _check_prestamos_y_novedades(
        self, estudiante_id: int, tipo_nombre: str
    ) -> dict:
        tipo = self.session.exec(
            select(TipoInventario).where(col(TipoInventario.nombre).ilike(tipo_nombre))
        ).first()
        if not tipo:
            return {"ok": True, "detalle": f"Sin préstamos de {tipo_nombre}"}

        prestamos = self.session.exec(
            select(Prestamo)
            .join(Inventario)
            .where(
                Prestamo.estudiante_id == estudiante_id,
                Inventario.tipo_inventario_id == tipo.id,
            )
        ).all()

        activos = [p for p in prestamos if p.estado_prestamo]
        if activos:
            return {
                "ok": False,
                "detalle": f"{len(activos)} préstamo(s) activo(s) sin devolver",
            }

        ids = [p.id for p in prestamos]
        if ids:
            novedades = self.session.exec(
                select(Novedad).where(
                    Novedad.prestamo_id.in_(ids),  # type: ignore[attr-defined]
                    Novedad.resuelta == False,  # noqa: E712
                )
            ).all()
            if novedades:
                return {
                    "ok": False,
                    "detalle": f"{len(novedades)} novedad(es) pendiente(s) de resolver",
                }

        return {"ok": True, "detalle": f"Sin novedades en {tipo_nombre}"}

    def check_chess(self, estudiante_id: int) -> dict:
        return self._check_prestamos_y_novedades(estudiante_id, "ajedrez")

    def check_band(self, estudiante_id: int) -> dict:
        return self._check_prestamos_y_novedades(estudiante_id, "banda")

    def check_sports(self, estudiante_id: int) -> dict:
        return self._check_prestamos_y_novedades(estudiante_id, "deporte")

    def check_training_schools(self, estudiante_id: int) -> dict:
        rows = self.session.execute(
            text(
                "SELECT id, activo, estado_escuela FROM detalleescuelaformacion "
                "WHERE estudiante_id = :eid AND activo = true"
            ),
            {"eid": estudiante_id},
        ).all()

        problemas: list[str] = []
        for r in rows:
            if not r.estado_escuela:
                problemas.append(f"Escuela ID {r.id}: estado pendiente")

        if problemas:
            return {"ok": False, "detalle": "; ".join(problemas)}
        return {"ok": True, "detalle": "Escuelas de formación al día"}

    def check_tests(self, estudiante_id: int) -> dict:
        pendientes = self.session.execute(
            text(
                "SELECT id, tipo_prueba FROM detalleprueba "
                "WHERE estudiante_id = :eid AND estado = false"
            ),
            {"eid": estudiante_id},
        ).all()
        if pendientes:
            return {
                "ok": False,
                "detalle": f"{len(pendientes)} prueba(s) sin pagar",
            }
        return {"ok": True, "detalle": "Pruebas pagadas"}

    # ── Estado de módulo para docente ───────────────────────────────────

    def check_rectoria(self, docente_id: int, periodo_id: int) -> dict:
        estado = self.session.exec(
            select(RectoriaEstado).where(
                RectoriaEstado.docente_id == docente_id,
            )
        ).first()

        if not estado:
            return {"ok": False, "detalle": "No tiene paz y salvo asignado en rectoría"}

        return {"ok": True, "detalle": f"Paz y Salvo: {estado.motivo_estado}"}

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
