from typing import Any

from app.core.db import SessionDep
from app.modules.webcolegios_import.domain.entities import (
    ImportSummary,
    ScrapedStudent,
    ScrapedTeacher,
)
from app.modules.webcolegios_import.domain.service import (
    WebcolegiosImportService,
    clean_text,
)
from app.modules.webcolegios_import.infrastructure.repository import (
    WebcolegiosImportRepository,
)


class BulkWebcolegiosLoad:
    def __init__(self, session: SessionDep) -> None:
        repository = WebcolegiosImportRepository(session)
        self.service = WebcolegiosImportService(repository)
        self.repository = repository

    def execute(self, tipo: str, records: list[dict[str, Any]]) -> ImportSummary:
        summary = ImportSummary()
        self.service.clear_staging()
        try:
            if tipo == "estudiante":
                students = [self._build_student(record) for record in records]
                summary.total_estudiantes_scrapeados = len(students)
                self.repository.save_staging_students(students)
                self.service.sync_students(summary)
                return summary

            if tipo == "docente":
                teachers = [self._build_teacher(record) for record in records]
                summary.total_docentes_scrapeados = len(teachers)
                self.repository.save_staging_teachers(teachers)
                self.service.sync_teachers(summary)
                return summary

            raise ValueError("Tipo de carga no soportado.")
        finally:
            self.service.clear_staging()

    def _build_student(self, record: dict[str, Any]) -> ScrapedStudent:
        return ScrapedStudent(
            nombre=clean_text(self._get(record, "nombre")),
            documento=clean_text(self._get(record, "documento")),
            grado_nombre=clean_text(
                self._get(record, "grado_nombre") or self._get(record, "grado")
            )
            or None,
            curso=clean_text(self._get(record, "curso")) or None,
            sede=clean_text(self._get(record, "sede")) or None,
            jornada=clean_text(self._get(record, "jornada")) or None,
            titular_nombre=clean_text(
                self._get(record, "titular_nombre") or self._get(record, "titular")
            )
            or None,
            acudiente_nombre=clean_text(self._get(record, "acudiente_nombre")) or None,
            acudiente_telefono=clean_text(self._get(record, "acudiente_telefono")) or None,
            acudiente_correo=clean_text(self._get(record, "acudiente_correo")) or None,
            raw_data=record,
        )

    def _build_teacher(self, record: dict[str, Any]) -> ScrapedTeacher:
        return ScrapedTeacher(
            nombre=clean_text(self._get(record, "nombre")),
            documento=clean_text(self._get(record, "documento")),
            asignatura=clean_text(self._get(record, "asignatura")) or "SIN ASIGNATURA",
            grado_titular=clean_text(self._get(record, "grado_titular")) or None,
            curso_titular=clean_text(self._get(record, "curso_titular")) or None,
            sede=clean_text(self._get(record, "sede")) or None,
            jornada=clean_text(self._get(record, "jornada")) or None,
            raw_data=record,
        )

    def _get(self, record: dict[str, Any], key: str) -> str | None:
        value = record.get(key)
        if value is None:
            return None
        return str(value)
