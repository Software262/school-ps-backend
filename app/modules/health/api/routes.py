from fastapi import APIRouter
from sqlmodel import select

from app.core.db import SessionDep

router = APIRouter(
    responses={
        200: {"description": "OK"},
    }
)


@router.get("")
async def health(session: SessionDep):
    session.exec(select(1))
    print("¡Ping exitoso! Conexión a la base de datos establecida.")
    return {"status": "ok"}
