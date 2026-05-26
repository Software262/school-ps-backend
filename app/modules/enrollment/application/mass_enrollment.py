import csv
import io

from sqlmodel import Session

from app.modules.enrollment.domain.service import EnrollmentService
from app.modules.enrollment.infrastructure.repository import (
    SQLEnrollmentRepository,
)


class MassEnrollment:
    """Caso de uso para registrar matrículas masivamente a partir de archivos."""

    def __init__(self, session: Session) -> None:
        repository = SQLEnrollmentRepository(session)
        self._service = EnrollmentService(repository)

    def execute(self, content: bytes, period_id: int, year: int) -> dict:
        decoded_content = content.decode("utf-8")
        reader = csv.reader(io.StringIO(decoded_content), delimiter=",")  # type: ignore[abstract]
        return self._process_rows(reader, period_id, year)

    def _process_rows(self, reader, period_id: int, year: int) -> dict:
        success_count = 0
        error_count = 0
        errors: list[str] = []

        header = next(reader, None)
        if not header:
            return {"status": "error", "message": "El archivo está vacío"}

        try:
            int(header[2])
            rows = [header] + list(reader)
        except (ValueError, IndexError):
            rows = list(reader)

        for line_idx, row in enumerate(rows, start=2):
            if not row or len(row) < 4:
                continue

            try:
                documento = row[0].strip()
                nombre = row[1].strip()
                grado_id = int(row[2].strip())
                acudiente_id = int(row[3].strip())

                student_id = self._service.find_or_create_student(
                    documento=documento,
                    nombre=nombre,
                    grado_id=grado_id,
                    acudiente_id=acudiente_id,
                )

                try:
                    self._service.register_enrollment(
                        student_id=student_id,
                        period_id=period_id,
                        year=year,
                    )
                    success_count += 1
                except ValueError as ve:
                    if "ya tiene" in str(ve):
                        pass
                    else:
                        raise ve

            except Exception as e:
                error_count += 1
                errors.append(f"Fila {line_idx} ({row}): {str(e)}")

        return {
            "status": "success" if error_count == 0 else "partial",
            "processed": success_count + error_count,
            "success": success_count,
            "errors": error_count,
            "error_details": errors[:10],
        }
