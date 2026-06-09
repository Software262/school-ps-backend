import json

from app.modules.webcolegios_import.domain.entities import ImportDetail, ImportSummary
from app.modules.webcolegios_import.domain.repositories import (
    WebcolegiosImportRepository,
)
from app.modules.webcolegios_import.domain.services import (
    clean_text,
    normalize_document,
    normalize_grade_name,
)
from app.modules.webcolegios_import.infrastructure.models import (
    WebcolegiosStagingStudent,
)
from app.modules.webcolegios_import.infrastructure.repository import (
    WEBCOLEGIOS_STUDENT_ENTITY,
)


class SyncStudents:
    def __init__(self, repository: WebcolegiosImportRepository):
        self.repository = repository

    def execute(self, summary: ImportSummary) -> ImportSummary:
        for student in self.repository.get_staging_students():
            self._sync_student(student, summary)
        return summary

    def _sync_student(
        self, student: WebcolegiosStagingStudent, summary: ImportSummary
    ) -> None:
        document = normalize_document(student.documento)
        name = clean_text(student.nombre)
        has_real_guardian = self._has_real_guardian_data(student)

        try:
            if not document or not name:
                self._register(
                    summary,
                    student,
                    "ERROR",
                    "Documento o nombre vac\u00edo en el registro scrapeado.",
                )
                summary.errores += 1
                return

            grade = self.repository.get_or_create_grade_by_name(student.grado_nombre)
            if not grade or grade.id is None:
                self._register(
                    summary,
                    student,
                    "PENDIENTE_DATOS",
                    self._build_missing_grade_observation(student),
                )
                summary.estudiantes_pendientes += 1
                return

            existing_student = self.repository.find_student_by_document(document)
            if existing_student:
                updates = []
                if existing_student.grado_id != grade.id:
                    existing_student = self.repository.update_student_grade(
                        existing_student,
                        grade.id,
                    )
                    updates.append(f"grado actualizado a '{grade.nombre}'")

                if has_real_guardian and self.repository.is_default_guardian(
                    existing_student.acudiente_id
                ):
                    guardian = self.repository.get_or_create_guardian(
                        student.acudiente_nombre,
                        student.acudiente_telefono,
                        student.acudiente_correo,
                    )
                    if guardian.id is None:
                        raise ValueError("No se pudo resolver el acudiente real.")

                    existing_student = self.repository.update_student_guardian(
                        existing_student,
                        guardian.id,
                    )
                    updates.append("acudiente real actualizado")

                if updates:
                    self._register(
                        summary,
                        student,
                        "ACTUALIZADO",
                        f"Estudiante existente actualizado: {', '.join(updates)}.",
                    )
                    summary.estudiantes_actualizados += 1
                    return

                observation = (
                    "El estudiante ya existe y conserva su acudiente actual."
                    if has_real_guardian
                    else "El estudiante ya existe en la tabla estudiante."
                )
                self._register(summary, student, "OMITIDO_EXISTENTE", observation)
                summary.estudiantes_omitidos += 1
                return

            guardian = (
                self.repository.get_or_create_guardian(
                    student.acudiente_nombre,
                    student.acudiente_telefono,
                    student.acudiente_correo,
                )
                if has_real_guardian
                else self.repository.get_or_create_default_guardian_na()
            )
            if guardian.id is None:
                raise ValueError("No se pudo resolver el acudiente.")

            self.repository.create_student(
                nombre=name,
                documento=document,
                grado_id=grade.id,
                acudiente_id=guardian.id,
            )
            self._register(
                summary,
                student,
                "INSERTADO",
                "Estudiante insertado desde WebColegios."
                if has_real_guardian
                else "Estudiante insertado con acudiente N/A temporal.",
            )
            summary.estudiantes_insertados += 1
        except Exception as exc:
            self._register(summary, student, "ERROR", f"Error al sincronizar: {exc}")
            summary.errores += 1

    def _has_real_guardian_data(self, student: WebcolegiosStagingStudent) -> bool:
        values = (
            student.acudiente_nombre,
            student.acudiente_telefono,
            student.acudiente_correo,
        )
        return any(
            clean_text(value) and clean_text(value).upper() != "N/A" for value in values
        )

    def _build_missing_grade_observation(
        self, student: WebcolegiosStagingStudent
    ) -> str:
        grade_webcolegios = clean_text(student.grado_nombre)
        grade_normalized = normalize_grade_name(grade_webcolegios)
        if not grade_normalized:
            return "No se pudo resolver grado. grado_webcolegios vac\u00edo o inv\u00e1lido."

        course = clean_text(student.curso)
        return (
            "No se pudo resolver grado. "
            f"grado_webcolegios='{grade_webcolegios}', "
            f"grado_normalizado='{grade_normalized}', "
            f"curso='{course}'"
        )

    def _register(
        self,
        summary: ImportSummary,
        student: WebcolegiosStagingStudent,
        estado: str,
        observacion: str,
    ) -> None:
        document = normalize_document(student.documento)
        name = clean_text(student.nombre)
        payload = {
            "nombre": name,
            "documento": document,
            "grado_nombre": student.grado_nombre,
            "grado_normalizado": normalize_grade_name(student.grado_nombre),
            "curso": student.curso,
            "sede": student.sede,
            "jornada": student.jornada,
            "titular_nombre": student.titular_nombre,
            "acudiente_nombre": student.acudiente_nombre,
        }

        self.repository.register_import_result(
            tipo_entidad=WEBCOLEGIOS_STUDENT_ENTITY,
            documento_identidad=document,
            datos=json.dumps(payload, ensure_ascii=False),
            estado=estado,
            observacion=observacion,
        )
        summary.detalle.append(
            ImportDetail(
                tipo="estudiante",
                documento=document,
                nombre=name,
                estado=estado,
                observacion=observacion,
            )
        )
