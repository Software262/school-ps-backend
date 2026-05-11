from sqlmodel import Field

from app.shared.infrastructure.base import Base


class tipoInventario(Base, table=True):
    nombre: str = Field(unique=True, index=True, nullable=False, max_length=50)
