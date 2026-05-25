"""
Rectoría Module Domain Service.

This module implements the PrincipalService containing the core business logic
validations for teacher administrative peace/safe statuses and observations.

Author: Yessyth Jaimes
Role: Product Owner and developer of the rectoria module
"""

from app.modules.principal.domain.repositories import PrincipalRepository
from app.modules.principal.schemas.request import (
    CreateObservationRequest,
    CreateStatusRequest,
    UpdateStatusRequest,
)


class PrincipalService:
    """
    Domain service to encapsulate core business rules and validations
    for the Rectoría module.
    """

    def __init__(self, repository: PrincipalRepository):
        """
        Initializes the service with a concrete repository.

        Args:
            repository (PrincipalRepository): Concrete repository dependency.
        """
        self.repository = repository

    async def get_teachers(self):
        """
        Retrieves all teachers with consolidated statuses and observations.

        Returns:
            list[dict]: A list of teacher records containing nested statuses and observations.
        """
        return await self.repository.get_teachers()

    async def create_observation(self, observation_data: CreateObservationRequest):
        """
        Validates and registers a new administrative observation.

        Args:
            observation_data (CreateObservationRequest): DTO containing observation details.

        Returns:
            RectoriaObservaciones: The newly created observation record.

        Raises:
            ValueError: If user, teacher, or period validations fail.
        """
        # Validate user existence
        user = await self.repository.get_user_by_id(observation_data.id_usuario)
        if not user:
            raise ValueError("El usuario no existe")

        # Validate user role
        if user.rol.lower() not in [
            "rectoría",
            "rectoria",
            "rector",
            "administrador",
            "administrador del sistema",
            "admin",
        ]:
            raise ValueError("El usuario no tiene permisos de Rectoría o Administrador")

        # Validate teacher existence
        teacher = await self.repository.get_teacher_by_id(observation_data.docente_id)
        if not teacher:
            raise ValueError("El docente no existe")

        # Validate period existence
        period = await self.repository.get_period_by_id(observation_data.periodo_id)
        if not period:
            raise ValueError("El periodo no existe")

        return await self.repository.create_observation(observation_data)

    async def create_status(self, status_data: CreateStatusRequest):
        """
        Validates and assigns a new administrative status to a teacher.

        Args:
            status_data (CreateStatusRequest): DTO containing status details.

        Returns:
            RectoriaEstado: The newly created administrative status record.

        Raises:
            ValueError: If user, teacher, period, or duplicate status checks fail.
        """
        # Validate user existence
        user = await self.repository.get_user_by_id(status_data.id_usuario)
        if not user:
            raise ValueError("El usuario no existe")

        # Validate user role
        if user.rol.lower() not in [
            "rectoría",
            "rectoria",
            "rector",
            "administrador",
            "administrador del sistema",
            "admin",
        ]:
            raise ValueError("El usuario no tiene permisos de Rectoría o Administrador")

        # Validate teacher existence
        teacher = await self.repository.get_teacher_by_id(status_data.docente_id)
        if not teacher:
            raise ValueError("El docente no existe")

        # Validate period existence
        period = await self.repository.get_period_by_id(status_data.periodo_id)
        if not period:
            raise ValueError("El periodo no existe")

        # Validate duplicate status check
        existing = await self.repository.get_status_by_docente_and_period(
            status_data.docente_id, status_data.periodo_id
        )
        if existing:
            raise ValueError(
                "Ya existe un estado administrativo para ese docente y periodo"
            )

        return await self.repository.create_status(status_data)

    async def update_status(self, status_id: int, status_data: UpdateStatusRequest):
        """
        Validates and updates an existing administrative status.

        Args:
            status_id (int): Unique identifier of the status record.
            status_data (UpdateStatusRequest): DTO containing updated status details.

        Returns:
            RectoriaEstado | None: The updated administrative status record, or None if not found.

        Raises:
            ValueError: If user existence or authorization checks fail.
        """
        # Retrieve the existing status
        status = await self.repository.get_status_by_id(status_id)
        if not status:
            return None

        # Validate user existence
        user = await self.repository.get_user_by_id(status_data.id_usuario)
        if not user:
            raise ValueError("El usuario no existe")

        # Validate user role
        if user.rol.lower() not in [
            "rectoría",
            "rectoria",
            "rector",
            "administrador",
            "administrador del sistema",
            "admin",
        ]:
            raise ValueError("El usuario no tiene permisos de Rectoría o Administrador")

        return await self.repository.update_status(status, status_data)
