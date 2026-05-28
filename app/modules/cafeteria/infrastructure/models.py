"""
Cafeteria Module Infrastructure Models.

This file defines the database schema using SQLModel.
Following the reviewer's feedback, all business logic (like @property)
has been moved to the service layer to keep the model as a pure data structure.

Author: Danilo Castillejo
Role: Developer of the cafeteria module
"""

from sqlmodel import Field
from app.shared.infrastructure.base import Base


class Cafeteria(Base, table=True):
    """
    Represents the cafeteria debt status for a student in a specific period.

    Attributes:
        estudiante_id: Link to the student. Indexed for faster lookups.
        periodo_id: Link to the academic year/period.
        usuario_id: The staff member responsible for the last update.
        estado_cafeteria: Binary state (True = Paz y Salvo, False = Debt/Blocked).
    """

    estudiante_id: int = Field(foreign_key="estudiante.id", index=True)
    periodo_id: int = Field(foreign_key="periodo.id", index=True)
    usuario_id: int | None = Field(default=None, foreign_key="usuario.id")

    # Default is True (Paz y Salvo) as per the operational flow requirements.
    estado_cafeteria: bool = Field(default=True)
    observaciones: str | None = Field(default=None, max_length=400)
