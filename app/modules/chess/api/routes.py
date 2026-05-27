from fastapi import APIRouter, status
from app.core.db import SessionDep
from app.shared.utils.response import Response
from app.modules.inventory.infrastructure.repository import InventoryRepository
from app.modules.chess.domain.service import ChessService
from app.modules.chess.schemas.request import ReturnChessRequest
from app.modules.chess.schemas.response import ReturnChessResponse

router = APIRouter(tags=["Chess"])


@router.patch("/borrow/{borrow_id}/return", status_code=status.HTTP_200_OK)
async def return_chess_borrowing(
    session: SessionDep, borrow_id: int, return_request: ReturnChessRequest
):
    repo = InventoryRepository(session=session)
    service = ChessService(repository=repo)

    data = await service.return_chess_borrow(borrow_id, return_request)

    return Response(
        data=ReturnChessResponse(**data),  # type: ignore
        message=str(data["mensaje"]),
        status_code=status.HTTP_200_OK,
        details={"novedad_creada": bool(data["novedad_creada"])},
    ).to_dict()
