"""
Rectoría Module Infrastructure Repository.

This module implements the concrete PrincipalRepository which communicates with
the database using SQLModel and SQLAlchemy to perform CRUD operations for
teachers, observations, statuses, and audit records, enforcing constraints.

Author: Yessyth Jaimes
Role: Product Owner and developer of the rectoria module
"""

from datetime import datetime
from sqlmodel import col, select, or_

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

    async def get_teachers(
        self,
    ) -> list[tuple[Docente, RectoriaEstado | None, RectoriaObservaciones | None]]:
        """
        Retrieves all teachers registered in the database, including their consolidated
        administrative peace and safe statuses and observations.

        Returns:
            list[tuple[Docente, RectoriaEstado | None, RectoriaObservaciones | None]]:
                A list of tuples, where each tuple represents a row with a Docente,
                their RectoriaEstado (if any), and RectoriaObservaciones (if any).
        """
        statement = (
            select(Docente, RectoriaEstado, RectoriaObservaciones)
            .join(
                RectoriaEstado,
                col(RectoriaEstado.docente_id) == col(Docente.id),
                isouter=True,
            )
            .join(
                RectoriaObservaciones,
                col(RectoriaObservaciones.docente_id) == col(Docente.id),
                isouter=True,
            )
            .order_by(col(Docente.id))
        )
        results = self.session.execute(statement).all()
        return [(r[0], r[1], r[2]) for r in results]

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
        """
        assert observation_data.periodo_id is not None
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

        assert observation_data.id_usuario is not None
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
        and registers an audit trail.

        Args:
            status_data (CreateStatusRequest): Object containing docente_id, periodo_id,
                id_usuario, and motivo_estado.

        Returns:
            RectoriaEstado: The newly created administrative status record.
        """
        assert status_data.periodo_id is not None
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

        assert status_data.id_usuario is not None
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
        """
        valor_anterior = status.motivo_estado
        status.motivo_estado = status_data.motivo_estado
        status.fecha_actualizacion = datetime.utcnow()

        self.session.add(status)
        self.session.commit()
        self.session.refresh(status)

        if status.id is None:
            raise ValueError("Failed to generate status ID")

        assert status_data.id_usuario is not None
        self._register_audit(
            id_usuario=status_data.id_usuario,
            tabla_nombre=RectoriaEstado.__name__,
            registro_id=status.id,
            operacion="UPDATE",
            valor_anterior=valor_anterior,
            valor_nuevo=status.motivo_estado,
        )

        return status

    async def get_user_by_id(self, user_id: int) -> Usuario | None:
        """
        Retrieves a user by their unique identifier.

        Args:
            user_id (int): Unique identifier of the user.

        Returns:
            Usuario | None: The user entity if found, otherwise None.
        """
        return self.session.get(Usuario, user_id)

    async def get_teacher_by_id(self, teacher_id: int) -> Docente | None:
        """
        Retrieves a teacher by their unique identifier.

        Args:
            teacher_id (int): Unique identifier of the teacher.

        Returns:
            Docente | None: The teacher entity if found, otherwise None.
        """
        return self.session.get(Docente, teacher_id)

    async def get_period_by_id(self, period_id: int) -> Periodo | None:
        """
        Retrieves an academic period by its unique identifier.

        Args:
            period_id (int): Unique identifier of the academic period.

        Returns:
            Periodo | None: The academic period entity if found, otherwise None.
        """
        return self.session.get(Periodo, period_id)

    async def get_active_period(self) -> Periodo | None:
        return self.session.exec(select(Periodo).where(col(Periodo.estado))).first()

    async def get_admin_user(self) -> Usuario | None:
        return self.session.exec(
            select(Usuario).where(
                col(Usuario.estado).is_(True),
                or_(
                    col(Usuario.rol).ilike("%rector%"),
                    col(Usuario.rol).ilike("%admin%"),
                ),
            )
        ).first()

    async def get_status_by_docente_and_period(
        self, docente_id: int, period_id: int
    ) -> RectoriaEstado | None:
        """
        Retrieves an administrative status by teacher and academic period.

        Args:
            docente_id (int): Unique identifier of the teacher.
            period_id (int): Unique identifier of the academic period.

        Returns:
            RectoriaEstado | None: The administrative status if found, otherwise None.
        """
        return self.session.exec(
            select(RectoriaEstado).where(
                RectoriaEstado.docente_id == docente_id,
                RectoriaEstado.periodo_id == period_id,
            )
        ).first()

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
        )

        self.session.add(audit)
        self.session.commit()
