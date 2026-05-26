from fastapi import APIRouter

router = APIRouter()


@router.get("/items")
async def get_all_instruments():
    return []
