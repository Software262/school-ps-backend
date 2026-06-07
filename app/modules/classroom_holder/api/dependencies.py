from fastapi import Depends, HTTPException, status
from pydantic import BaseModel


# =====================================================================
# NOTA PARA EL DESARROLLADOR:
# Reemplaza este mock con la importación real de tu módulo de Auth.
# Ejemplo: from app.modules.auth.api.dependencies import get_current_user
# =====================================================================
class UsuarioMock(BaseModel):
    id: int
    rol: str


def get_current_user_mock() -> UsuarioMock:
    # Simula un usuario logueado. Cambia "ESTUDIANTE" para probar el error 403.
    return UsuarioMock(id=1, rol="DOCENTE_TITULAR")


# =====================================================================


def verificar_acceso_salon_titular(
    current_user: UsuarioMock = Depends(
        get_current_user_mock
    ),  # <-- Cambiar por get_current_user real
) -> UsuarioMock:
    """
    Dependencia que verifica si el usuario actual tiene el rol adecuado
    para acceder al módulo de Salón Titular.
    """
    roles_permitidos = ["ADMINISTRADOR", "DOCENTE_TITULAR"]

    if current_user.rol not in roles_permitidos:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso Restringido. Este módulo está disponible únicamente para docentes titulares y administradores.",
        )

    return current_user
