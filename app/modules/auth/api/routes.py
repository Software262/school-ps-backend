from fastapi import APIRouter, HTTPException, status

from app.core.db import SessionDep
from app.modules.auth.application.login_user import LoginUser
from app.modules.auth.schemas.request import LoginRequest
from app.modules.auth.schemas.response import LoginResponse, UserResponse

router = APIRouter(
    responses={
        200: {"description": "OK"},
        401: {"description": "No autorizado"},
    },
)


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=200,
    summary="Iniciar sesión y obtener rol del usuario",
    description="Autentica a un usuario y retorna su rol y token de sesión.",
)
async def login(
    session: SessionDep,
    request: LoginRequest,
) -> LoginResponse:
    use_case = LoginUser(session=session)

    try:
        user, token, rol = use_case.execute(request)
    except ValueError as e:
        error_msg = str(e)
        if "incorrectos" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_msg,
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        ) from e

    if user.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al procesar el usuario: ID no asignado",
        )
    return LoginResponse(
        mensaje="Inicio de sesión exitoso",
        usuario=UserResponse(
            id=user.id,
            username=user.username,
            rol=rol,
            estado=user.estado,
        ),
        token=token,
    )
