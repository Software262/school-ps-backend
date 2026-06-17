"""
Rectoría Module Domain Service.

This module implements the PrincipalService containing the core business logic
validations for teacher administrative peace/safe statuses and observations.

Author: Yessyth Jaimes
Role: Product Owner and developer of the rectoria module
"""

from typing import Any

from app.modules.auth.infrastructure.models import Usuario
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

    async def get_teachers(self) -> list[dict]:
        """
        Retrieves all teachers with consolidated statuses and observations.

        Returns:
            list[dict]: A list of teacher records containing nested statuses and observations.
        """
        results = await self.repository.get_teachers()

        teachers_map: dict[int, dict[str, Any]] = {}
        for docente, estado, observacion in results:
            docente_id = docente.id
            if docente_id is None:
                continue

            if docente_id not in teachers_map:
                teachers_map[docente_id] = {
                    "id": docente_id,
                    "nombre": docente.nombre,
                    "documento": docente.documento,
                    "estado": docente.estado,
                    "asignatura": docente.asignatura,
                    "estados_administrativos": {},
                    "observaciones": {},
                }

            t_data = teachers_map[docente_id]
            if (
                estado
                and estado.id is not None
                and estado.id not in t_data["estados_administrativos"]
            ):
                t_data["estados_administrativos"][estado.id] = {
                    "id": estado.id,
                    "periodo_id": estado.periodo_id,
                    "motivo_estado": estado.motivo_estado,
                    "fecha_actualizacion": estado.fecha_actualizacion.isoformat()
                    if estado.fecha_actualizacion
                    else None,
                }
            if (
                observacion
                and observacion.id is not None
                and observacion.id not in t_data["observaciones"]
            ):
                t_data["observaciones"][observacion.id] = {
                    "id": observacion.id,
                    "periodo_id": observacion.periodo_id,
                    "descripcion": observacion.descripcion,
                    "tipo_observacion": observacion.tipo_observacion,
                    "fecha": observacion.fecha.isoformat()
                    if observacion.fecha
                    else None,
                }

        # Convert dict of dicts to list of lists
        teachers_list = []
        for t_id in sorted(teachers_map.keys()):
            t_data = teachers_map[t_id]
            t_data["estados_administrativos"] = list(
                t_data["estados_administrativos"].values()
            )
            t_data["observaciones"] = list(t_data["observaciones"].values())
            teachers_list.append(t_data)

        return teachers_list

    async def _resolve_periodo_id(self, periodo_id: int | None) -> int:
        if periodo_id is not None:
            period = await self.repository.get_period_by_id(periodo_id)
            if not period:
                raise ValueError("El periodo no existe")
            return periodo_id

        active = await self.repository.get_active_period()
        if not active or active.id is None:
            raise ValueError("No hay un periodo activo configurado")
        return active.id

    async def _resolve_usuario_id(self, usuario_id: int | None) -> int:
        if usuario_id is not None:
            user = await self.repository.get_user_by_id(usuario_id)
            if not user:
                raise ValueError("El usuario no existe")
            return usuario_id

        admin = await self.repository.get_admin_user()
        if not admin or admin.id is None:
            raise ValueError("No se encontró un usuario administrador o de rectoría")
        return admin.id

    async def _validate_user_role(self, user_id: int) -> Usuario:
        user = await self.repository.get_user_by_id(user_id)
        if not user:
            raise ValueError("El usuario no existe")
        if user.rol.lower() not in [
            "rectoría",
            "rectoria",
            "rector",
            "administrador",
            "administrador del sistema",
            "admin",
        ]:
            raise ValueError("El usuario no tiene permisos de Rectoría o Administrador")
        return user

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
        # Resolve user (use admin if not provided)
        resolved_usuario_id = await self._resolve_usuario_id(
            observation_data.id_usuario
        )
        await self._validate_user_role(resolved_usuario_id)

        # Validate teacher existence
        teacher = await self.repository.get_teacher_by_id(observation_data.docente_id)
        if not teacher:
            raise ValueError("El docente no existe")

        # Resolve period (use active if not provided)
        resolved_periodo_id = await self._resolve_periodo_id(
            observation_data.periodo_id
        )

        observation_data.id_usuario = resolved_usuario_id
        observation_data.periodo_id = resolved_periodo_id
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
        # Resolve user (use admin if not provided)
        resolved_usuario_id = await self._resolve_usuario_id(status_data.id_usuario)
        await self._validate_user_role(resolved_usuario_id)

        # Validate teacher existence
        teacher = await self.repository.get_teacher_by_id(status_data.docente_id)
        if not teacher:
            raise ValueError("El docente no existe")

        # Resolve period (use active if not provided)
        resolved_periodo_id = await self._resolve_periodo_id(status_data.periodo_id)

        # Validate duplicate status check
        existing = await self.repository.get_status_by_docente_and_period(
            status_data.docente_id, resolved_periodo_id
        )
        if existing:
            raise ValueError(
                "Ya existe un estado administrativo para ese docente y periodo"
            )

        status_data.id_usuario = resolved_usuario_id
        status_data.periodo_id = resolved_periodo_id
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

        # Resolve user (use admin if not provided)
        resolved_usuario_id = await self._resolve_usuario_id(status_data.id_usuario)
        await self._validate_user_role(resolved_usuario_id)

        status_data.id_usuario = resolved_usuario_id
        return await self.repository.update_status(status, status_data)
