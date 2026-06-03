from abc import ABC, abstractmethod
from app.modules.auth.infrastructure.models import Usuario


class AuthRepository(ABC):
    """Interfaz abstracta para el repositorio de autenticación."""

    @abstractmethod
    def get_user_by_credentials(
        self, username: str, contrasenia: str
    ) -> Usuario | None:
        """Obtiene un usuario por sus credenciales."""
        ...
