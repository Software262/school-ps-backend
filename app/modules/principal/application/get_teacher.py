"""
Rectoría Module Get Teachers Use Case.

This module contains the application use case for retrieving a list of all teachers,
including their consolidated administrative statuses and observations.

Author: Yessyth Jaimes
Role: Product Owner and developer of the rectoria module
"""

from app.core.db import SessionDep
from app.modules.principal.domain.service import PrincipalService
from app.modules.principal.infrastructure.repository import (
    PrincipalRepository,
)


class GetTeachers:
    """
    Use case to handle retrieving all teachers with their consolidated Rectoría details.
    """

    def __init__(self, session: SessionDep):
        """
        Initializes the use case with a database session to instantiate service and repository dependencies.

        Args:
            session (SessionDep): SQLModel Database session.
        """
        self.repository = PrincipalRepository(session=session)

        self.service = PrincipalService(repository=self.repository)

    async def execute(self):
        """
        Executes the business logic to retrieve all teachers with their administrative status and observations.

        Returns:
            list[dict]: A list of teacher records containing nested lists for statuses and observations.
        """
        return await self.service.get_teachers()
