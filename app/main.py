from fastapi import FastAPI

from app.core.config import get_settings
from app.modules import router

get_settings()

app = FastAPI()

app.include_router(router)
