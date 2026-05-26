"""
Rectoría Module Create Observation Use Case.

This module contains the application use case for creating a new administrative
observation for a teacher.

Author: Yessyth Jaimes
Role: Product Owner and developer of the rectoria module
"""

from app.core.db import SessionDep
from app.modules.principal.domain.service import PrincipalService
from app.modules.principal.infrastructure.repository import (
    PrincipalRepository,
)
from app.modules.principal.schemas.request import (
    CreateObservationRequest,
)


class CreateObservation:
    """
    Use case to handle the creation of an administrative observation for a teacher.
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
        observation_data: CreateObservationRequest,
    ):
        """
        Executes the business logic to create an administrative observation.

        Args:
            observation_data (CreateObservationRequest): DTO containing teacher, period, user details,
                and observation content.

        Returns:
            RectoriaObservaciones: The newly created observation database record.

        Raises:
            ValueError: If validation checks for existing entities or user permissions fail.
        """
        return await self.service.create_observation(observation_data)
