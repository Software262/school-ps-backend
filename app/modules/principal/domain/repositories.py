"""
Rectoría Module Domain Repository Interface.

This module defines the abstract interface PrincipalRepository, which outlines
the contracts for administrative observations and statuses data access.

Author: Yessyth Jaimes
Role: Product Owner and developer of the rectoria module
"""

from abc import ABC, abstractmethod

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
    """
    Abstract base class representing the data repository contract for the Rectoría module.
    """

    @abstractmethod
    async def get_teachers(self):
        """
        Retrieves all teachers with consolidated statuses and observations.

        Returns:
            list[dict]: A list of teacher records containing nested statuses and observations.
        """
        pass

    @abstractmethod
    async def create_observation(
        self,
        observation_data: CreateObservationRequest,
    ) -> PrincipalObservation:
        """
        Registers a new administrative observation for a teacher.

        Args:
            observation_data (CreateObservationRequest): DTO containing observation details.

        Returns:
            PrincipalObservation: The newly created observation database entity.
        """
        pass

    @abstractmethod
    async def create_status(
        self,
        status_data: CreateStatusRequest,
    ) -> PrincipalStatus:
        """
        Assigns a new administrative status to a teacher.

        Args:
            status_data (CreateStatusRequest): DTO containing status details.

        Returns:
            PrincipalStatus: The newly created status database entity.
        """
        pass

    @abstractmethod
    async def get_status_by_id(
        self,
        status_id: int,
    ) -> PrincipalStatus | None:
        """
        Retrieves an administrative status by its unique ID.

        Args:
            status_id (int): Unique identifier of the status record.

        Returns:
            PrincipalStatus | None: The status record if found, otherwise None.
        """
        pass

    @abstractmethod
    async def update_status(
        self,
        status: PrincipalStatus,
        status_data: UpdateStatusRequest,
    ) -> PrincipalStatus:
        """
        Updates an existing administrative status record.

        Args:
            status (PrincipalStatus): The existing status record to update.
            status_data (UpdateStatusRequest): DTO containing updated status details.

        Returns:
            PrincipalStatus: The updated status database entity.
        """
        pass
