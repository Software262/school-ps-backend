from abc import ABC, abstractmethod
from typing import Sequence

from app.modules.principal.infrastructure.models import (
    PrincipalObservation,
    PrincipalStatus,
)

from app.modules.principal.schemas.request import (
    CreateObservationRequest,
    CreateStatusRequest,
    UpdateStatusRequest,
)


class PrincipalRepository(ABC):

    @abstractmethod
    async def get_teachers(self):
        pass

    @abstractmethod
    async def create_observation(
        self,
        observation_data: CreateObservationRequest,
    ) -> PrincipalObservation:
        pass

    @abstractmethod
    async def create_status(
        self,
        status_data: CreateStatusRequest,
    ) -> PrincipalStatus:
        pass

    @abstractmethod
    async def get_status_by_id(
        self,
        status_id: int,
    ) -> PrincipalStatus | None:
        pass

    @abstractmethod
    async def update_status(
        self,
        status: PrincipalStatus,
        status_data: UpdateStatusRequest,
    ) -> PrincipalStatus:
        pass