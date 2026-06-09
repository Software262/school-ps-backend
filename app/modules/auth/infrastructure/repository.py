from sqlmodel import select

from app.core.db import SessionDep
from app.modules.auth.domain.repositories import AuthRepository
from app.modules.auth.infrastructure.models import Usuario


class SQLAuthRepository(AuthRepository):
    """Implementación concreta del repositorio usando SQLModel."""

    def __init__(self, session: SessionDep) -> None:
        self._session = session

    def get_user_by_credentials(
        self, username: str, contrasenia: str
    ) -> Usuario | None:
        statement = select(Usuario).where(
            Usuario.username == username,
            Usuario.contrasenia == contrasenia,
        )
        return self._session.exec(statement).first()
