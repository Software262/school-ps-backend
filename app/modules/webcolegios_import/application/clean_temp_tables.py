from app.modules.webcolegios_import.domain.repositories import (
    WebcolegiosImportRepository,
)


class CleanWebcolegiosTempTables:
    def __init__(self, repository: WebcolegiosImportRepository):
        self.repository = repository

    def execute(self) -> None:
        self.repository.clear_staging()
