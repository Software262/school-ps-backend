from fastapi import APIRouter, status
from app.core.db import SessionDep
from app.shared.utils.response import Response
from app.modules.chess.schemas.request import ReturnChessRequest
from app.modules.chess.schemas.response import ReturnChessResponse
from app.modules.chess.application.return_chess_borrowing import ReturnChessBorrowing

router = APIRouter()


@router.patch("/borrow/{borrow_id}/return", status_code=status.HTTP_200_OK)
async def return_chess_borrowing(
    session: SessionDep, borrow_id: int, return_request: ReturnChessRequest
):
    app_service = ReturnChessBorrowing(session=session)
    result = await app_service.execute(borrow_id, return_request)

    if result.get("error"):
        status_code = (
            status.HTTP_404_NOT_FOUND
            if result["error"] == "NOT_FOUND"
            else status.HTTP_400_BAD_REQUEST
        )
        return Response(
            data=None,
            message="Error al procesar la devolución de ajedrez",
            status_code=status_code,
            details={"message": result["message"]},
        ).to_dict()

    data = result["data"]

    response_data = ReturnChessResponse(
        id=data["id"],
        estado_prestamo=data["estado_prestamo"],
        novedad_creada=data["novedad_creada"],
        mensaje=data["mensaje"],
    )

    return Response(
        data=response_data,
        message=str(data["mensaje"]),
        status_code=status.HTTP_200_OK,
        details={"novedad_creada": bool(data["novedad_creada"])},
    ).to_dict()
