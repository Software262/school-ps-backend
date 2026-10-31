from app.core.db import SessionDep
from app.modules.principal.domain.service import PrincipalService
from app.modules.principal.infrastructure.repository import (
    PrincipalRepository,
)


class DeleteObservation:
    """
    Use case to handle the deletion of an administrative observation for a teacher.
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
        observation_id: int,
        id_usuario: int | None = None,
    ):
        """
        Executes the business logic to delete an administrative observation following the 24-hour limit.

        Args:
            observation_id (int): Identifier of the observation to delete.
            id_usuario (int | None): Identifier of the user performing the action.

        Returns:
            bool | None: True if deletion was successful, None if observation was not found.

        Raises:
            ValueError: If user lacks permissions or 24 hours have passed.
        """
        return await self.service.delete_observation(
            observation_id=observation_id,
            id_usuario=id_usuario,
        )