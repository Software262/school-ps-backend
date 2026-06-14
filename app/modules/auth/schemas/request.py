from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Esquema de solicitud de inicio de sesión."""

    username: str = Field(min_length=3, description="Nombre de usuario")
    contrasenia: str = Field(min_length=3, description="Contraseña en texto plano")
