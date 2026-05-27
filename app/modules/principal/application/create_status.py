"""
Rectoría Module Create Status Use Case.

This module contains the application use case for assigning a new administrative
status (paz y salvo) to a teacher.

Author: Yessyth Jaimes
Role: Product Owner and developer of the rectoria module
"""

from app.core.db import SessionDep
from app.modules.principal.domain.service import PrincipalService
from app.modules.principal.infrastructure.repository import (
    PrincipalRepository,
)
from app.modules.principal.schemas.request import (
    CreateStatusRequest,
)


class CreateStatus:
    """
    Use case to handle assigning a new administrative status to a teacher.
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
        status_data: CreateStatusRequest,
    ):
        """
        Executes the business logic to assign an administrative status to a teacher.

        Args:
            status_data (CreateStatusRequest): DTO containing teacher, period, user details,
                and status motivation.

        Returns:
            RectoriaEstado: The newly created status database record.

        Raises:
            ValueError: If validation checks for existing entities, user permissions, or duplicate records fail.
        """
        return await self.service.create_status(status_data)
