import json
from typing import Any

from app.core.db import SessionDep
from app.modules.webcolegios_import.domain.entities import (
    ImportDetail,
    ImportSummary,
    ScrapedStudent,
)
from app.modules.webcolegios_import.domain.repositories import (
    WEBCOLEGIOS_STUDENT_ENTITY,
)
from app.modules.webcolegios_import.domain.service import (
    WebcolegiosImportService,
    clean_text,
    normalize_document,
)
from app.modules.webcolegios_import.infrastructure.repository import (
    WebcolegiosImportRepository,
)


class ReprocessPendingStudents:
    def __init__(self, session: SessionDep) -> None:
        self.repository = WebcolegiosImportRepository(session)
        self.service = WebcolegiosImportService(self.repository)

    def execute(self) -> ImportSummary:
        pending_records = self.repository.get_pending_student_imports()
        summary = ImportSummary(total_estudiantes_scrapeados=len(pending_records))

        self.service.clear_staging()
        try:
            students = []
            for record in pending_records:
                try:
                    students.append(self._build_student(record))
                except Exception as exc:
                    self._register_error(summary, record, exc)

            if students:
                self.repository.save_staging_students(students)
                self.service.sync_students(summary)
                self._update_original_pending_records(pending_records, summary)

            return summary
        finally:
            self.service.clear_staging()

    def _build_student(self, record: Any) -> ScrapedStudent:
        payload = json.loads(record.datos)
        if not isinstance(payload, dict):
            raise ValueError("El campo datos no contiene un objeto JSON.")

        raw_data = {
            **payload,
            "reprocesado_desde_importacionautomatica_id": record.id,
        }
        return ScrapedStudent(
            nombre=clean_text(self._get(payload, "nombre")),
            documento=clean_text(
                self._get(payload, "documento")
                or self._string(record.documento_identidad)
            ),
            grado_nombre=clean_text(
                self._get(payload, "grado_nombre") or self._get(payload, "grado")
            )
            or None,
            curso=clean_text(self._get(payload, "curso")) or None,
            sede=clean_text(self._get(payload, "sede")) or None,
            jornada=clean_text(self._get(payload, "jornada")) or None,
            titular_nombre=clean_text(
                self._get(payload, "titular_nombre") or self._get(payload, "titular")
            )
            or None,
            acudiente_nombre=clean_text(self._get(payload, "acudiente_nombre")) or None,
            acudiente_telefono=clean_text(self._get(payload, "acudiente_telefono"))
            or None,
            acudiente_correo=clean_text(self._get(payload, "acudiente_correo")) or None,
            raw_data=raw_data,
        )

    def _register_error(
        self, summary: ImportSummary, record: Any, exc: Exception
    ) -> None:
        document = self._string(record.documento_identidad)
        observation = f"Error al reprocesar pendiente: {exc}"
        self.repository.register_import_result(
            tipo_entidad=WEBCOLEGIOS_STUDENT_ENTITY,
            documento_identidad=document,
            datos=record.datos or "{}",
            estado="ERROR",
            observacion=observation,
        )
        summary.errores += 1
        summary.detalle.append(
            ImportDetail(
                tipo="estudiante",
                documento=document,
                nombre=None,
                estado="ERROR",
                observacion=observation,
            )
        )

    def _update_original_pending_records(
        self, pending_records: Any, summary: ImportSummary
    ) -> None:
        results_by_document = {
            detail.documento: detail
            for detail in summary.detalle
            if detail.tipo == "estudiante" and detail.documento
        }

        for record in pending_records:
            document = self._document_from_record(record)
            detail = results_by_document.get(document)
            if not detail:
                continue

            self.repository.update_import_result_status(
                record=record,
                estado=detail.estado,
                observacion=f"Pendiente reprocesado. {detail.observacion}",
            )

    def _document_from_record(self, record: Any) -> str:
        try:
            payload = json.loads(record.datos)
        except json.JSONDecodeError:
            payload = {}

        document = ""
        if isinstance(payload, dict):
            document = self._get(payload, "documento")
        return normalize_document(document or self._string(record.documento_identidad))

    def _get(self, payload: dict[str, Any], key: str) -> str:
        return self._string(payload.get(key))

    def _string(self, value: Any) -> str:
        if value is None:
            return ""
        return str(value)
