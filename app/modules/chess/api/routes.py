from fastapi import APIRouter, status
from app.core.db import SessionDep
from app.shared.utils.response import Response
from typing import Any, cast

from app.modules.chess.schemas.request import (
    CreateChessBorrowRequest,
    ReturnChessBorrowRequest,
    ResolveChessNoveltyRequest,
)

from app.modules.chess.application.create_borrowing import CreateChessBorrowing
from app.modules.chess.application.return_borrowing import ReturnChessBorrowing
from app.modules.chess.application.resolve_novelty import ResolveChessNovelty
from app.modules.chess.application.get_clearance import GetChessClearance

router = APIRouter()


@router.post("/borrow", status_code=status.HTTP_201_CREATED)
async def create_chess_borrow(
    session: SessionDep, request_data: CreateChessBorrowRequest
):
    app_service = CreateChessBorrowing(session=session)
    result = await app_service.execute(request_data)
    
    # If result is an error dict, handle it
    if isinstance(result, dict) and result.get("error"):
        status_code = status.HTTP_404_NOT_FOUND if result["error"] == "NOT_FOUND" else status.HTTP_400_BAD_REQUEST
        return Response(
            data=None,
            message="Error al .where(Prestamo.id == Novedad.prestamo_id)
            .where(Prestamo.estudiante_id == estudiante_id)
            .where(Novedad.resuelta.is_(False))",
            status_code=status_code,
            details={"error": result["message"]}
        ).to_dict()
    
    # At this point result is a Prestamo instance
    prestamo = result  # type: ignore[assignment]
    return Response(
        data={"prestamo_id": getattr(prestamo, "id", None)},
        message="Préstamo de ajedrez registrado exitosamente.",
        status_code=status.HTTP_201_CREATED
    ).to_dict()


@router.post("/return/{prestamo_id}", status_code=status.HTTP_200_OK)
async def return_chess_borrow(
    session: SessionDep, prestamo_id: int, request_data: ReturnChessBorrowRequest
):
    # En un entorno real user_id vendría del token. Aquí lo simulamos o pedimos por request.
    user_id = 1 
    app_service = ReturnChessBorrowing(session=session)
    result = await app_service.execute(prestamo_id, user_id, request_data)
    
    if isinstance(result, dict) and result.get("error"):
        status_code = status.HTTP_404_NOT_FOUND if result["error"] == "NOT_FOUND" else status.HTTP_400_BAD_REQUEST
        return Response(
            data=None,
            message="Error al procesar la devolución",
            status_code=status_code,
            details={"error": result["message"]}
        ).to_dict()
    
    from typing import cast, Any
    # Ensure result is a dict
    result_dict = cast(dict[str, Any], result)
    data_body = result_dict["data"]  # type: ignore[index]
    mensaje: str = data_body.get("mensaje", "")
    return Response(
        data=data_body,
        message=mensaje,
        status_code=status.HTTP_200_OK
    ).to_dict()


@router.post("/novelty/{novedad_id}/resolve", status_code=status.HTTP_200_OK)
async def resolve_chess_novelty(
    session: SessionDep, novedad_id: int, request_data: ResolveChessNoveltyRequest
):
    app_service = ResolveChessNovelty(session=session)
    result = await app_service.execute(novedad_id, request_data)

    if result.get("error"):
        return Response(
            data=None,
            message="Error al resolver la novedad",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"error": result["message"]}
        ).to_dict()

    # Safely extract data and message
    data_body = result["data"]  # type: ignore[index]
    mensaje: str = data_body.get("mensaje", "")
    return Response(
        data=data_body,
        message=mensaje,
        status_code=status.HTTP_200_OK
    ).to_dict()


@router.get("/clearance/{estudiante_id}", status_code=status.HTTP_200_OK)
async def get_chess_clearance(
    session: SessionDep, estudiante_id: int
):
    app_service = GetChessClearance(session=session)
    result = await app_service.execute(estudiante_id)
    # Ensure result is a dict for type checking
    result_dict = cast(dict[str, Any], result)
    return Response(
        data={"paz_y_salvo": result_dict["paz_y_salvo"]},
        message=result_dict["message"],  # type: ignore[index]
        status_code=status.HTTP_200_OK
    ).to_dict()
