from fastapi import APIRouter

router = APIRouter()

##
profesores = [
    "Profesor A",
    "Profesor B",]

@router.get("/profesores")
async def get_all_profesores():
    return profesores
