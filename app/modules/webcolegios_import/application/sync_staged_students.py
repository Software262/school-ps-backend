from app.core.db import SessionDep
from app.modules.webcolegios_import.domain.entities import ImportSummary
from app.modules.webcolegios_import.domain.service import WebcolegiosImportService
from app.modules.webcolegios_import.infrastructure.repository import (
    WebcolegiosImportRepository,
)


class SyncStagedStudents:
    def __init__(self, session: SessionDep) -> None:
        repository = WebcolegiosImportRepository(session)
        self.service = WebcolegiosImportService(repository)
        self.repository = repository

    def execute(self) -> ImportSummary:
        summary = ImportSummary(
            total_estudiantes_scrapeados=len(self.repository.get_staging_students())
        )
        try:
            self.service.sync_students(summary)
            return summary
        finally:
            self.service.clear_staging()
