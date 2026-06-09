import json

from app.modules.webcolegios_import.domain.entities import ImportDetail, ImportSummary
from app.modules.webcolegios_import.domain.repositories import (
    WebcolegiosImportRepository,
)
from app.modules.webcolegios_import.domain.services import (
    clean_text,
    normalize_document,
)
from app.modules.webcolegios_import.infrastructure.models import (
    WebcolegiosStagingTeacher,
)
from app.modules.webcolegios_import.infrastructure.repository import (
    WEBCOLEGIOS_TEACHER_ENTITY,
)


class SyncTeachers:
    def __init__(self, repository: WebcolegiosImportRepository):
        self.repository = repository

    def execute(self, summary: ImportSummary) -> ImportSummary:
        for teacher in self.repository.get_staging_teachers():
            self._sync_teacher(teacher, summary)
        return summary

    def _sync_teacher(
        self, teacher: WebcolegiosStagingTeacher, summary: ImportSummary
    ) -> None:
        document = normalize_document(teacher.documento)
        name = clean_text(teacher.nombre)
        subject = clean_text(teacher.asignatura) or "SIN ASIGNATURA"

        try:
            if not name:
                self._register(
                    summary,
                    teacher,
                    "ERROR",
                    "Nombre vacio en el registro scrapeado.",
                )
                summary.errores += 1
                return

            existing_teacher_by_name = self.repository.find_teacher_by_name(name)
            existing_document = (
                normalize_document(existing_teacher_by_name.documento)
                if existing_teacher_by_name
                else ""
            )
            if existing_teacher_by_name and existing_document:
                teacher.documento = existing_document
                self._register(
                    summary,
                    teacher,
                    "OMITIDO_EXISTENTE",
                    "El docente titular ya existe en la tabla docente.",
                )
                summary.docentes_omitidos += 1
                return

            if not document:
                self._register(
                    summary,
                    teacher,
                    "PENDIENTE_DATOS",
                    self._build_missing_document_observation(teacher, name),
                )
                return

            if self.repository.find_teacher_by_document(document):
                self._register(
                    summary,
                    teacher,
                    "OMITIDO_EXISTENTE",
                    "El docente ya existe en la tabla docente.",
                )
                summary.docentes_omitidos += 1
                return

            self.repository.create_teacher(name, document, subject)
            self._register(
                summary,
                teacher,
                "INSERTADO",
                "Docente insertado desde WebColegios.",
            )
            summary.docentes_insertados += 1
        except Exception as exc:
            self._register(summary, teacher, "ERROR", f"Error al sincronizar: {exc}")
            summary.errores += 1

    def _build_missing_document_observation(
        self, teacher: WebcolegiosStagingTeacher, name: str
    ) -> str:
        grade = clean_text(teacher.grado_titular)
        course = clean_text(teacher.curso_titular)
        return (
            "No se pudo resolver documento del titular. "
            f"titular_nombre='{name}', grado='{grade}', curso='{course}'"
        )

    def _register(
        self,
        summary: ImportSummary,
        teacher: WebcolegiosStagingTeacher,
        estado: str,
        observacion: str,
    ) -> None:
        document = normalize_document(teacher.documento)
        name = clean_text(teacher.nombre)
        payload = {
            "nombre": name,
            "documento": document,
            "asignatura": clean_text(teacher.asignatura) or "SIN ASIGNATURA",
            "grado_titular": teacher.grado_titular,
            "curso_titular": teacher.curso_titular,
            "sede": teacher.sede,
            "jornada": teacher.jornada,
        }

        self.repository.register_import_result(
            tipo_entidad=WEBCOLEGIOS_TEACHER_ENTITY,
            documento_identidad=document,
            datos=json.dumps(payload, ensure_ascii=False),
            estado=estado,
            observacion=observacion,
        )
        summary.detalle.append(
            ImportDetail(
                tipo="docente",
                documento=document,
                nombre=name,
                estado=estado,
                observacion=observacion,
            )
        )
