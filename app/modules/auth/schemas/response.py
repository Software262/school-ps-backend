from pydantic import BaseModel


class UserResponse(BaseModel):
    """Información básica del usuario."""

    id: int
    username: str
    rol: str
    estado: bool


class LoginResponse(BaseModel):
    """Esquema de respuesta exitosa de inicio de sesión."""

    mensaje: str
    usuario: UserResponse
    token: str
