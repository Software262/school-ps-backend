from app.modules.peace_safe.domain.repositories import PeaceSafeRepository
from app.modules.peace_safe.schemas.response import (
    DocenteInfo,
    EstudianteInfo,
    GenerateResponse,
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

    # ── Verificaciones individuales (lógica de negocio) ───────────────

    def _check_matricula(self, estudiante_id: int, periodo_id: int) -> ModuloStatus:
        matricula = self.repo.get_matricula(estudiante_id, periodo_id)
        if not matricula:
            return ModuloStatus(
                clave="enrollment",
                nombre="Matrícula",
                estado="ok",
                detalle="Estudiante matriculado",
            )

        if matricula.estado_matricula != "paz_y_salvo":
            return ModuloStatus(
                clave="enrollment",
                nombre="Matrícula",
                estado="error",
                detalle="Matrícula pendiente de pago",
            )

        assert matricula.id is not None
        detalles = self.repo.get_matricula_detalles(matricula.id)
        if detalles:
            total = sum(d.valor_pendiente for d in detalles)
            return ModuloStatus(
                clave="enrollment",
                nombre="Matrícula",
                estado="error",
                detalle=f"Pendiente de pago: ${total:,}",
            )

        return ModuloStatus(
            clave="enrollment",
            nombre="Matrícula",
            estado="ok",
            detalle="Matrícula pagada",
        )

    def _check_pension(self, estudiante_id: int) -> ModuloStatus:
        pension = self.repo.get_pension(estudiante_id)
        if not pension:
            return ModuloStatus(
                clave="tuition",
                nombre="Pensión",
                estado="ok",
                detalle="Sin pensión registrada",
            )

        if not pension.estado_pension:
            return ModuloStatus(
                clave="tuition",
                nombre="Pensión",
                estado="error",
                detalle="Pensión con estado pendiente",
            )

        return ModuloStatus(
            clave="tuition", nombre="Pensión", estado="ok", detalle="Pensión al día"
        )

    def _check_cafeteria(self, estudiante_id: int, periodo_id: int) -> ModuloStatus:
        cafeteria = self.repo.get_cafeteria(estudiante_id, periodo_id)
        if cafeteria and not cafeteria.estado_cafeteria:
            return ModuloStatus(
                clave="cafeteria",
                nombre="Cafetería",
                estado="error",
                detalle="Deuda en cafetería",
            )

        return ModuloStatus(
            clave="cafeteria",
            nombre="Cafetería",
            estado="ok",
            detalle="Sin deudas en cafetería",
        )

    def _check_pupitre(self, estudiante_id: int) -> ModuloStatus:
        pupitre = self.repo.get_pupitre_by_student(estudiante_id)
        if pupitre and not pupitre.estado:
            obs = pupitre.observacion or "Sin detalles"
            return ModuloStatus(
                clave="pupitre",
                nombre="Pupitre",
                estado="error",
                detalle=f"Pupitre no devuelto: {obs}",
            )

        return ModuloStatus(
            clave="pupitre", nombre="Pupitre", estado="ok", detalle="Pupitre en orden"
        )

    def _check_observador(self, estudiante_id: int) -> ModuloStatus:
        rows = self.repo.get_observaciones(estudiante_id)
        if rows:
            tipos = list(set(r.tipo_incidencia for r in rows))
            return ModuloStatus(
                clave="observador",
                nombre="Observaciones del salón",
                estado="error",
                detalle=f"Incidencias registradas: {', '.join(tipos)} ({len(rows)})",
            )

        return ModuloStatus(
            clave="observador",
            nombre="Observaciones del salón",
            estado="ok",
            detalle="Sin incidencias registradas",
        )

    def _check_loans(
        self, estudiante_id: int, tipo_nombre: str, clave: str, nombre: str
    ) -> ModuloStatus:
        prestamos, novedades = self.repo.get_loans_by_type(estudiante_id, tipo_nombre)

        activos = [p for p in prestamos if p.estado_prestamo]
        if activos:
            return ModuloStatus(
                clave=clave,
                nombre=nombre,
                estado="error",
                detalle=f"{len(activos)} préstamo(s) activo(s) sin devolver",
            )

        if novedades:
            return ModuloStatus(
                clave=clave,
                nombre=nombre,
                estado="error",
                detalle=f"{len(novedades)} novedad(es) pendiente(s) de resolver",
            )

        return ModuloStatus(
            clave=clave,
            nombre=nombre,
            estado="ok",
            detalle=f"Sin novedades en {nombre}",
        )

    def _check_chess(self, estudiante_id: int) -> ModuloStatus:
        return self._check_loans(estudiante_id, "ajedrez", "chess", "Ajedrez")

    def _check_band(self, estudiante_id: int) -> ModuloStatus:
        return self._check_loans(estudiante_id, "banda", "band", "Banda Musical")

    def _check_sports(self, estudiante_id: int) -> ModuloStatus:
        return self._check_loans(estudiante_id, "deporte", "sports", "Deportes")

    def _check_training_schools(self, estudiante_id: int) -> ModuloStatus:
        rows = self.repo.get_training_school_details(estudiante_id)

        problemas: list[str] = []
        for r in rows:
            if not r.estado_escuela:
                problemas.append(f"Escuela ID {r.id}: estado pendiente")

        if problemas:
            return ModuloStatus(
                clave="training_schools",
                nombre="Esc. Formación",
                estado="error",
                detalle="; ".join(problemas),
            )

        return ModuloStatus(
            clave="training_schools",
            nombre="Esc. Formación",
            estado="ok",
            detalle="Escuelas de formación al día",
        )

    def _check_tests(self, estudiante_id: int) -> ModuloStatus:
        pendientes = self.repo.get_test_details(estudiante_id)
        if pendientes:
            return ModuloStatus(
                clave="tests",
                nombre="Pruebas",
                estado="error",
                detalle=f"{len(pendientes)} prueba(s) sin pagar",
            )

        return ModuloStatus(
            clave="tests", nombre="Pruebas", estado="ok", detalle="Pruebas pagadas"
        )

    def _check_rectoria(self, docente_id: int, periodo_id: int) -> ModuloStatus:
        estado = self.repo.get_rectoria_status(docente_id)

        if not estado:
            return ModuloStatus(
                clave="rectoria",
                nombre="Rectoría",
                estado="error",
                detalle="No tiene paz y salvo asignado en rectoría",
            )

        return ModuloStatus(
            clave="rectoria",
            nombre="Rectoría",
            estado="ok",
            detalle=f"Paz y Salvo: {estado.motivo_estado}",
        )

    # ── Métodos principales ───────────────────────────────────────────

    def get_student_status(self, estudiante_id: int) -> StatusResponse | None:
        estudiante = self.repo.get_student(estudiante_id)
        if not estudiante:
            return None

        grado_nombre = (
            self.repo.get_grade_name(estudiante.grado_id)
            if estudiante.grado_id
            else None
        )

        periodo = self.repo.get_active_period()
        periodo_id = int(periodo.id) if periodo else 0

        assert estudiante.id is not None
        entidad = EstudianteInfo(
            id=estudiante.id,
            nombre=estudiante.nombre,
            documento=estudiante.documento,
            grado=grado_nombre or "",
        )

        modulos: list[ModuloStatus] = []
        for clave, nombre, method_name in STUDENT_MODULES:
            method = getattr(self, f"_{method_name}")
            try:
                if clave in ("cafeteria", "enrollment"):
                    result = method(estudiante_id, periodo_id)
                else:
                    result = method(estudiante_id)
            except Exception as e:
                result = ModuloStatus(
                    clave=clave,
                    nombre=nombre,
                    estado="error",
                    detalle=f"Error al consultar: {e}",
                )
            modulos.append(result)

        ok_count = sum(1 for m in modulos if m.estado == "ok")
        total = len(modulos)

        return StatusResponse(
            entidad=entidad,
            modulos=modulos,
            total_modulos=total,
            modulos_ok=ok_count,
            modulos_error=total - ok_count,
            paz_y_salvo=ok_count == total,
        )

    def get_teacher_status(self, docente_id: int) -> StatusResponse | None:
        docente = self.repo.get_teacher(docente_id)
        if not docente:
            return None

        periodo = self.repo.get_active_period()
        periodo_id = periodo.id if periodo else 0

        assert docente.id is not None
        entidad = DocenteInfo(
            id=docente.id,
            nombre=docente.nombre,
            documento=docente.documento,
            asignatura=docente.asignatura,
        )

        modulos: list[ModuloStatus] = []
        for clave, nombre, method_name in TEACHER_MODULES:
            method = getattr(self, f"_{method_name}")
            try:
                result = method(docente_id, periodo_id)
            except Exception as e:
                result = ModuloStatus(
                    clave=clave,
                    nombre=nombre,
                    estado="error",
                    detalle=f"Error al consultar: {e}",
                )
            modulos.append(result)

        ok_count = sum(1 for m in modulos if m.estado == "ok")
        total = len(modulos)

        return StatusResponse(
            entidad=entidad,
            modulos=modulos,
            total_modulos=total,
            modulos_ok=ok_count,
            modulos_error=total - ok_count,
            paz_y_salvo=ok_count == total,
        )

    def generate_student_pazysalvo(
        self, estudiante_id: int, usuario_id: int
    ) -> GenerateResponse | None:
        status = self.get_student_status(estudiante_id)
        if not status:
            return None

        if not status.paz_y_salvo:
            raise ValueError("El estudiante no está a paz y salvo en todos los módulos")

        periodo = self.repo.get_active_period()
        periodo_id = int(periodo.id) if periodo else 0

        detalles = [
            {
                "modulo": m.clave,
                "nombre": m.nombre,
                "estado": m.estado,
                "detalle": m.detalle,
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

        assert record.id is not None
        return GenerateResponse(
            id=record.id,
            codigo=record.codigo_certificado,
            estado_final=record.estado_final,
            fecha=record.fecha_generacion.isoformat()
            if record.fecha_generacion
            else "",
            entidad={
                "nombre": status.entidad.nombre,
                "documento": status.entidad.documento,
                "grado": getattr(status.entidad, "grado", None),
            },
            periodo={
                "id": periodo_id,
                "nombre": f"Periodo {periodo_id}",
            },
            detalles=detalles,
        )

    def generate_teacher_pazysalvo(
        self, docente_id: int, usuario_id: int
    ) -> GenerateResponse | None:
        status = self.get_teacher_status(docente_id)
        if not status:
            return None

        if not status.paz_y_salvo:
            raise ValueError("El docente no está a paz y salvo en rectoría")

        periodo = self.repo.get_active_period()
        periodo_id = int(periodo.id) if periodo else 0
        periodo_nombre = (
            periodo.periodo_electivo.isoformat()
            if periodo and periodo.periodo_electivo
            else f"Periodo {periodo_id}"
        )

        detalles = [
            {
                "modulo": m.clave,
                "nombre": m.nombre,
                "estado": m.estado,
                "detalle": m.detalle,
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

        assert record.id is not None
        return GenerateResponse(
            id=record.id,
            codigo=record.codigo_certificado,
            estado_final=record.estado_final,
            fecha=record.fecha_generacion.isoformat()
            if record.fecha_generacion
            else "",
            entidad={
                "nombre": status.entidad.nombre,
                "documento": status.entidad.documento,
            },
            periodo={
                "id": periodo_id,
                "nombre": periodo_nombre,
            },
            detalles=detalles,
        )

    def search_students(self, query: str) -> list[dict]:
        students = self.repo.search_students(query)
        return [
            {
                "id": s.id,
                "nombre": s.nombre,
                "documento": s.documento,
            }
            for s in students
        ]

    def search_teachers(self, query: str) -> list[dict]:
        teachers = self.repo.search_teachers(query)
        return [
            {
                "id": t.id,
                "nombre": t.nombre,
                "documento": t.documento,
                "asignatura": t.asignatura,
            }
            for t in teachers
        ]

    def get_detail_status(self, pazysalvo_id: int) -> dict | None:
        record = self.repo.get_pazysalvo(pazysalvo_id)
        if not record:
            return None

        detalles = self.repo.get_detalles(pazysalvo_id)

        if record.entidad_tipo == "estudiante":
            estudiante = self.repo.get_student(record.entidad_id)
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
            docente = self.repo.get_teacher(record.entidad_id)
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
