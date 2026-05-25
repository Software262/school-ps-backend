"""
Rectoría Module Infrastructure Repository.

This module implements the concrete PrincipalRepository which communicates with
the database using SQLModel and SQLAlchemy to perform CRUD operations for
teachers, observations, statuses, and audit records, enforcing constraints.

Author: Yessyth Jaimes
Role: Product Owner and developer of the rectoria module
"""

from datetime import datetime

from sqlalchemy import text
from sqlmodel import select

from app.core.db import SessionDep
from app.modules.enrollment.infrastructure.models import Docente, Periodo
from app.modules.auth.infrastructure.models import Usuario
from app.modules.principal.domain.repositories import (
    PrincipalRepository as PrincipalRepositoryInterface,
)
from app.modules.principal.infrastructure.models import (
    Auditoria,
    RectoriaEstado,
    RectoriaObservaciones,
)
from app.modules.principal.schemas.request import (
    CreateObservationRequest,
    CreateStatusRequest,
    UpdateStatusRequest,
)


class PrincipalRepository(PrincipalRepositoryInterface):
    """
    Concrete repository implementation for the Principal (Rectoría) module.

    Handles database query and command execution for teacher observations,
    administrative statuses, and auditing.
    """

    def __init__(self, session: SessionDep):
        """
        Initializes the repository with a database session.

        Args:
            session (SessionDep): SQLModel Session injected dependency.
        """
        self.session = session

    async def get_teachers(self) -> list[dict]:
        """
        Retrieves all teachers registered in the database, including their consolidated
        administrative peace and safe statuses and observations.

        Returns:
            list[dict]: A list of dictionaries, where each dictionary represents a teacher
                and contains nested lists for their administrative statuses and observations.
        """
        query = text("SELECT * FROM docente ORDER BY id")
        result = self.session.execute(query)
        teachers = [dict(row) for row in result.mappings().all()]

        for teacher in teachers:
            teacher_id = teacher["id"]
            # Fetch statuses
            status_query = select(RectoriaEstado).where(
                RectoriaEstado.docente_id == teacher_id
            )
            statuses = self.session.exec(status_query).all()
            teacher["estados_administrativos"] = [
                {
                    "id": s.id,
                    "periodo_id": s.periodo_id,
                    "motivo_estado": s.motivo_estado,
                    "fecha_actualizacion": s.fecha_actualizacion.isoformat()
                    if s.fecha_actualizacion
                    else None,
                }
                for s in statuses
            ]

            # Fetch observations
            obs_query = select(RectoriaObservaciones).where(
                RectoriaObservaciones.docente_id == teacher_id
            )
            observations = self.session.exec(obs_query).all()
            teacher["observaciones"] = [
                {
                    "id": o.id,
                    "periodo_id": o.periodo_id,
                    "descripcion": o.descripcion,
                    "tipo_observacion": o.tipo_observacion,
                    "fecha": o.fecha.isoformat() if o.fecha else None,
                }
                for o in observations
            ]
        return teachers

    async def create_observation(
        self,
        observation_data: CreateObservationRequest,
    ) -> RectoriaObservaciones:
        """
        Creates and stores a new administrative observation for a teacher, and registers
        an audit trail of the action.

        Args:
            observation_data (CreateObservationRequest): Object containing docente_id,
                periodo_id, id_usuario, descripcion, and tipo_observacion.

        Returns:
            RectoriaObservaciones: The newly created administrative observation record.

        Raises:
            ValueError: If the user does not exist, does not have Rectoría/Admin privileges,
                if the docente does not exist, or if the academic period does not exist.
        """
        # Validations
        usuario = self.session.get(Usuario, observation_data.id_usuario)
        if not usuario:
            raise ValueError("El usuario no existe")
        if usuario.rol.lower() not in [
            "rectoría",
            "rectoria",
            "rector",
            "administrador",
            "administrador del sistema",
            "admin",
        ]:
            raise ValueError("El usuario no tiene permisos de Rectoría o Administrador")

        docente = self.session.get(Docente, observation_data.docente_id)
        if not docente:
            raise ValueError("El docente no existe")

        periodo = self.session.get(Periodo, observation_data.periodo_id)
        if not periodo:
            raise ValueError("El periodo no existe")

        new_observation = RectoriaObservaciones(
            docente_id=observation_data.docente_id,
            periodo_id=observation_data.periodo_id,
            descripcion=observation_data.descripcion,
            tipo_observacion=observation_data.tipo_observacion,
            fecha=datetime.utcnow(),
        )

        self.session.add(new_observation)
        self.session.commit()
        self.session.refresh(new_observation)

        if new_observation.id is None:
            raise ValueError("Failed to generate observation ID")

        self._register_audit(
            id_usuario=observation_data.id_usuario,
            tabla_nombre=RectoriaObservaciones.__name__,
            registro_id=new_observation.id,
            operacion="INSERT",
            valor_anterior="",
            valor_nuevo=(
                f"descripcion={new_observation.descripcion}; "
                f"tipo_observacion={new_observation.tipo_observacion}"
            ),
        )

        return new_observation

    async def create_status(
        self,
        status_data: CreateStatusRequest,
    ) -> RectoriaEstado:
        """
        Creates and stores a new administrative status for a teacher in a specific academic period,
        provided that one does not already exist, and registers an audit trail.

        Args:
            status_data (CreateStatusRequest): Object containing docente_id, periodo_id,
                id_usuario, and motivo_estado.

        Returns:
            RectoriaEstado: The newly created administrative status record.

        Raises:
            ValueError: If the user does not exist, does not have Rectoría/Admin privileges,
                if the docente does not exist, if the academic period does not exist, or if
                an administrative status already exists for that teacher and period.
        """
        # Validations
        usuario = self.session.get(Usuario, status_data.id_usuario)
        if not usuario:
            raise ValueError("El usuario no existe")
        if usuario.rol.lower() not in [
            "rectoría",
            "rectoria",
            "rector",
            "administrador",
            "administrador del sistema",
            "admin",
        ]:
            raise ValueError("El usuario no tiene permisos de Rectoría o Administrador")

        docente = self.session.get(Docente, status_data.docente_id)
        if not docente:
            raise ValueError("El docente no existe")

        periodo = self.session.get(Periodo, status_data.periodo_id)
        if not periodo:
            raise ValueError("El periodo no existe")

        existing_status = self.session.exec(
            select(RectoriaEstado).where(
                RectoriaEstado.docente_id == status_data.docente_id,
                RectoriaEstado.periodo_id == status_data.periodo_id,
            )
        ).first()

        if existing_status:
            raise ValueError(
                "Ya existe un estado administrativo para ese docente y periodo"
            )

        new_status = RectoriaEstado(
            docente_id=status_data.docente_id,
            periodo_id=status_data.periodo_id,
            motivo_estado=status_data.motivo_estado,
            fecha_actualizacion=datetime.utcnow(),
        )

        self.session.add(new_status)
        self.session.commit()
        self.session.refresh(new_status)

        if new_status.id is None:
            raise ValueError("Failed to generate status ID")

        self._register_audit(
            id_usuario=status_data.id_usuario,
            tabla_nombre=RectoriaEstado.__name__,
            registro_id=new_status.id,
            operacion="INSERT",
            valor_anterior="",
            valor_nuevo=new_status.motivo_estado,
        )

        return new_status

    async def get_status_by_id(self, status_id: int) -> RectoriaEstado | None:
        """
        Retrieves a teacher's administrative status record by its unique identifier.

        Args:
            status_id (int): The unique ID of the administrative status record.

        Returns:
            RectoriaEstado | None: The status record if found, otherwise None.
        """
        return self.session.get(RectoriaEstado, status_id)

    async def update_status(
        self,
        status: RectoriaEstado,
        status_data: UpdateStatusRequest,
    ) -> RectoriaEstado:
        """
        Updates an existing administrative status record with new details and logs the
        modification in the audit trail.

        Args:
            status (RectoriaEstado): The existing administrative status record to update.
            status_data (UpdateStatusRequest): Object containing the new motivo_estado
                and the id_usuario performing the update.

        Returns:
            RectoriaEstado: The updated administrative status record.

        Raises:
            ValueError: If the user performing the update does not exist or lacks
                sufficient Rectoría/Admin privileges.
        """
        # Validations
        usuario = self.session.get(Usuario, status_data.id_usuario)
        if not usuario:
            raise ValueError("El usuario no existe")
        if usuario.rol.lower() not in [
            "rectoría",
            "rectoria",
            "rector",
            "administrador",
            "administrador del sistema",
            "admin",
        ]:
            raise ValueError("El usuario no tiene permisos de Rectoría o Administrador")

        valor_anterior = status.motivo_estado
        status.motivo_estado = status_data.motivo_estado
        status.fecha_actualizacion = datetime.utcnow()

        self.session.add(status)
        self.session.commit()
        self.session.refresh(status)

        if status.id is None:
            raise ValueError("Failed to generate status ID")

        self._register_audit(
            id_usuario=status_data.id_usuario,
            tabla_nombre=RectoriaEstado.__name__,
            registro_id=status.id,
            operacion="UPDATE",
            valor_anterior=valor_anterior,
            valor_nuevo=status.motivo_estado,
        )

        return status

    def _register_audit(
        self,
        id_usuario: int,
        tabla_nombre: str,
        registro_id: int,
        operacion: str,
        valor_anterior: str,
        valor_nuevo: str,
    ) -> None:
        """
        Internal helper method to log an action into the system audit trail.

        Args:
            id_usuario (int): The ID of the user executing the operation.
            tabla_nombre (str): The name of the table being modified.
            registro_id (int): The ID of the modified table row.
            operacion (str): The operation type (e.g. INSERT, UPDATE, DELETE).
            valor_anterior (str): String representation of the record before the modification.
            valor_nuevo (str): String representation of the record after the modification.
        """
        audit = Auditoria(
            id_usuario=id_usuario,
            tabla_nombre=tabla_nombre,
            registro_id=registro_id,
            operacion=operacion,
            valor_anterior=valor_anterior,
            valor_nuevo=valor_nuevo,
            fecha_accion=datetime.utcnow(),
        )

        self.session.add(audit)
        self.session.commit()
