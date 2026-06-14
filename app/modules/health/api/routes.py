from fastapi import APIRouter, status
from sqlmodel import select

from app.core.db import SessionDep
from app.core.logger import setup_logger
from app.shared.utils.response import Response

logger = setup_logger()

router = APIRouter(
    responses={
        200: {"description": "OK"},
    }
)


@router.get("")
async def health(session: SessionDep):
    session.exec(select(1))

    logger.info("¡Ping exitoso! Conexión a la base de datos establecida.")

    return Response(data={"status": "ok"}, status_code=status.HTTP_200_OK)
