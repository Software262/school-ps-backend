from app.core.db import SessionDep
from app.modules.auth.domain.service import AuthService
from app.modules.auth.infrastructure.models import Usuario
from app.modules.auth.infrastructure.repository import SQLAuthRepository
from app.modules.auth.schemas.request import LoginRequest


class LoginUser:
    """Caso de uso: autenticar un usuario y validar su rol."""

    def __init__(self, session: SessionDep) -> None:
        repository = SQLAuthRepository(session)
        self._service = AuthService(repository)

    def execute(self, request: LoginRequest) -> tuple[Usuario, str, str]:
        return self._service.authenticate(request.username, request.contrasenia)
