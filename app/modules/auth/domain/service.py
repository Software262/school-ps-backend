from app.modules.auth.domain.repositories import AuthRepository
from app.modules.auth.infrastructure.models import Usuario


class AuthService:
    """Servicio de dominio para la autenticación y roles de usuario."""

    def __init__(self, repository: AuthRepository) -> None:
        self.repo = repository

    def authenticate(self, username: str, contrasenia: str) -> tuple[Usuario, str, str]:
        """Autentica a un usuario y genera su token y rol normalizado."""
        user = self.repo.get_user_by_credentials(username, contrasenia)

        if not user:
            msg = "Nombre de usuario o contraseña incorrectos"
            raise ValueError(msg)

        if not user.estado:
            msg = "El usuario se encuentra inactivo"
            raise ValueError(msg)

        # Normalizar el rol a uno de los 4 permitidos: Rectoría, Administración, Tesorería, Docente
        role_lower = user.rol.lower().strip()
        if "rector" in role_lower:
            normalized_role = "Rectoría"
        elif "docente" in role_lower:
            normalized_role = "Docente"
        elif (
            "tesor" in role_lower
            or "matrícula" in role_lower
            or "matricula" in role_lower
            or "paz" in role_lower
        ):
            normalized_role = "Tesorería"
        else:
            normalized_role = "Administración"

        # Generamos un token de sesión sencillo
        token = f"session_token_{normalized_role}_{user.username}_{user.id}"

        return user, token, normalized_role
