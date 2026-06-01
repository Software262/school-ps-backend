"""
Rectoría Module Update Status Use Case.

This module contains the application use case for updating an existing administrative
status (paz y salvo) record for a teacher.

Author: Yessyth Jaimes
Role: Product Owner and developer of the rectoria module
"""

from app.core.db import SessionDep
from app.modules.principal.domain.service import PrincipalService
from app.modules.principal.infrastructure.repository import (
    PrincipalRepository,
)
from app.modules.principal.schemas.request import (
    UpdateStatusRequest,
)


class UpdateStatus:
    """
    Use case to handle updating an existing administrative status record.
    """

    def __init__(self, session: SessionDep):
        """
        Initializes the use case with a database session to instantiate service and repository dependencies.

        Args:
            session (SessionDep): SQLModel Database session.
        """
        self.repository = PrincipalRepository(session=session)

        self.service = PrincipalService(repository=self.repository)

    async def execute(
        self,
        status_id: int,
        status_data: UpdateStatusRequest,
    ):
        """
        Executes the business logic to update an administrative status record.

        Args:
            status_id (int): The unique ID of the administrative status record to update.
            status_data (UpdateStatusRequest): DTO containing the new motivation and updating user ID.

        Returns:
            RectoriaEstado | None: The updated status record if found, otherwise None.

        Raises:
            ValueError: If validation checks for existing entities or user permissions fail.
        """
        return await self.service.update_status(
            status_id,
            status_data,
        )
