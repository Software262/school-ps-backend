from app.modules.principal.domain.repositories import PrincipalRepository

from app.modules.principal.schemas.request import (
    CreateObservationRequest,
    CreateStatusRequest,
    UpdateStatusRequest,
)


class PrincipalService:
    def __init__(self, repository: PrincipalRepository):
        self.repository = repository

    async def get_teachers(self):
        return await self.repository.get_teachers()

    async def create_observation(
        self,
        observation_data: CreateObservationRequest,
    ):

        return await self.repository.create_observation(observation_data)

    async def create_status(
        self,
        status_data: CreateStatusRequest,
    ):

        return await self.repository.create_status(status_data)

    async def update_status(
        self,
        status_id: int,
        status_data: UpdateStatusRequest,
    ):

        status = await self.repository.get_status_by_id(status_id)

        if not status:
            return None

        return await self.repository.update_status(
            status,
            status_data,
        )
