from fastapi import APIRouter

router = APIRouter()

instruments = [
    "Guitar",
    "Bass",
    "Drums",
    "Vocals",
]


@router.get("/instruments")
async def get_all_instruments():
    return instruments
