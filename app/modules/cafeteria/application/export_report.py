from app.core.db import SessionDep
from app.modules.cafeteria.domain.service import CafeteriaService
from app.modules.cafeteria.infrastructure.enrollment_adapter import (
    CafeteriaEnrollmentAdapter,
)
from app.modules.cafeteria.infrastructure.repository import CafeteriaRepository


def _escape_pdf_text(value: object) -> str:
    text = str(value).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return text.encode("latin-1", errors="replace").decode("latin-1")


def _text_line(x: int, y: int, text: object, size: int = 9) -> str:
    return f"BT /F1 {size} Tf {x} {y} Td ({_escape_pdf_text(text)}) Tj ET\n"


def _build_pdf(rows: list[list[str]]) -> bytes:
    page_contents: list[str] = []
    rows_per_page = 32
    header = ["DOCUMENTO", "ESTUDIANTE", "CURSO", "ESTADO", "OBSERVACIONES"]

    for page_start in range(0, max(len(rows), 1), rows_per_page):
        content = _text_line(50, 760, "Reporte de Cafeteria", 16)
        content += _text_line(50, 740, "Deudores activos por periodo", 10)
        y = 710
        for x, title in zip((50, 120, 280, 360, 430), header, strict=True):
            content += _text_line(x, y, title, 8)
        y -= 18

        page_rows = rows[page_start : page_start + rows_per_page]
        if not page_rows:
            content += _text_line(50, y, "No hay registros de deuda para mostrar.", 10)
        for row in page_rows:
            values = [
                row[0][:14],
                row[1][:28],
                row[2][:14],
                row[3][:12],
                row[4][:28],
            ]
            for x, value in zip((50, 120, 280, 360, 430), values, strict=True):
                content += _text_line(x, y, value, 8)
            y -= 20
        page_contents.append(content)

    objects: dict[int, bytes] = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        3: b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
    }
    page_refs: list[str] = []
    next_id = 4

    for content in page_contents:
        content_bytes = content.encode("latin-1", errors="replace")
        content_id = next_id
        page_id = next_id + 1
        objects[content_id] = (
            f"<< /Length {len(content_bytes)} >>\nstream\n".encode("ascii")
            + content_bytes
            + b"endstream"
        )
        objects[page_id] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 3 0 R >> >> "
            f"/Contents {content_id} 0 R >>"
        ).encode("ascii")
        page_refs.append(f"{page_id} 0 R")
        next_id += 2

    objects[2] = (
        f"<< /Type /Pages /Kids [{' '.join(page_refs)}] /Count {len(page_refs)} >>"
    ).encode("ascii")

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for object_id in sorted(objects):
        offsets.append(len(pdf))
        pdf.extend(f"{object_id} 0 obj\n".encode("ascii"))
        pdf.extend(objects[object_id])
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF".encode("ascii")
    )
    return bytes(pdf)


class ExportReport:
    def __init__(self, session: SessionDep):
        self.service = CafeteriaService(
            repository=CafeteriaRepository(session),
            student_service=CafeteriaEnrollmentAdapter(session),
        )

    async def execute(self, periodo_id: int) -> bytes:
        data_rows = await self.service.format_report_data(periodo_id)
        return _build_pdf(data_rows)
