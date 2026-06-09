from typing import Any

from app.modules.webcolegios_import.application.clean_temp_tables import (
    CleanWebcolegiosTempTables,
)
from app.modules.webcolegios_import.application.sync_students import SyncStudents
from app.modules.webcolegios_import.application.sync_teachers import SyncTeachers
from app.modules.webcolegios_import.domain.entities import (
    ImportSummary,
    ScrapedStudent,
    ScrapedTeacher,
)
from app.modules.webcolegios_import.domain.repositories import (
    WebcolegiosImportRepository,
)
from app.modules.webcolegios_import.domain.services import clean_text


class ManualWebcolegiosLoad:
    def __init__(self, repository: WebcolegiosImportRepository):
        self.repository = repository

    def execute_bulk(self, tipo: str, records: list[dict[str, Any]]) -> ImportSummary:
        return self._execute(tipo=tipo, records=records)

    def execute_single(self, tipo: str, record: dict[str, Any]) -> ImportSummary:
        return self._execute(tipo=tipo, records=[record])

    def sync_staged_students(self) -> ImportSummary:
        summary = ImportSummary(
            total_estudiantes_scrapeados=len(self.repository.get_staging_students())
        )
        try:
            SyncStudents(self.repository).execute(summary)
            return summary
        finally:
            CleanWebcolegiosTempTables(self.repository).execute()

    def _execute(self, tipo: str, records: list[dict[str, Any]]) -> ImportSummary:
        summary = ImportSummary()
        cleaner = CleanWebcolegiosTempTables(self.repository)

        cleaner.execute()
        try:
            if tipo == "estudiante":
                students = [self._build_student(record) for record in records]
                summary.total_estudiantes_scrapeados = len(students)
                self.repository.save_staging_students(students)
                SyncStudents(self.repository).execute(summary)
                return summary

            if tipo == "docente":
                teachers = [self._build_teacher(record) for record in records]
                summary.total_docentes_scrapeados = len(teachers)
                self.repository.save_staging_teachers(teachers)
                SyncTeachers(self.repository).execute(summary)
                return summary

            raise ValueError("Tipo de carga no soportado.")
        finally:
            cleaner.execute()

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
            acudiente_telefono=clean_text(self._get(record, "acudiente_telefono"))
            or None,
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
