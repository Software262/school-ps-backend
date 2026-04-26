from fastapi import APIRouter

router = APIRouter(
    responses={
        200: {"description": "OK"},
    }
)


@router.get("")
async def health():
    return {"status": "ok"}
