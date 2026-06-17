"""
Rectoría Module Domain Repository Interface.

This module defines the abstract interface PrincipalRepository, which outlines
the contracts for administrative observations and statuses data access.

Author: Yessyth Jaimes
Role: Product Owner and developer of the rectoria module
"""

from abc import ABC, abstractmethod

from app.modules.auth.infrastructure.models import Usuario
from app.modules.enrollment.infrastructure.models import Docente, Periodo
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
    async def get_teachers(
        self,
    ) -> list[tuple[Docente, PrincipalStatus | None, PrincipalObservation | None]]:
        """
        Retrieves all teachers with consolidated statuses and observations.

        Returns:
            list[tuple[Docente, PrincipalStatus | None, PrincipalObservation | None]]:
                A list of tuples containing the Docente, their administrative status,
                and observation.
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

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> Usuario | None:
        """
        Retrieves a user by their unique identifier.

        Args:
            user_id (int): Unique identifier of the user.

        Returns:
            Usuario | None: The user entity if found, otherwise None.
        """
        pass

    @abstractmethod
    async def get_teacher_by_id(self, teacher_id: int) -> Docente | None:
        """
        Retrieves a teacher by their unique identifier.

        Args:
            teacher_id (int): Unique identifier of the teacher.

        Returns:
            Docente | None: The teacher entity if found, otherwise None.
        """
        pass

    @abstractmethod
    async def get_period_by_id(self, period_id: int) -> Periodo | None:
        """
        Retrieves an academic period by its unique identifier.

        Args:
            period_id (int): Unique identifier of the academic period.

        Returns:
            Periodo | None: The academic period entity if found, otherwise None.
        """
        pass

    @abstractmethod
    async def get_status_by_docente_and_period(
        self, docente_id: int, period_id: int
    ) -> PrincipalStatus | None:
        """
        Retrieves an administrative status by teacher and academic period.

        Args:
            docente_id (int): Unique identifier of the teacher.
            period_id (int): Unique identifier of the academic period.

        Returns:
            PrincipalStatus | None: The administrative status if found, otherwise None.
        """
        pass

    @abstractmethod
    async def get_active_period(self) -> Periodo | None:
        """
        Retrieves the currently active academic period.

        Returns:
            Periodo | None: The active academic period if found, otherwise None.
        """
        pass

    @abstractmethod
    async def get_admin_user(self) -> Usuario | None:
        """
        Retrieves an active user with administrator or rectoría role.

        Returns:
            Usuario | None: An admin/rectoría user if found, otherwise None.
        """
        pass
