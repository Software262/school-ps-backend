from fastapi import FastAPI

from app.core.config import get_settings
from app.core.logger import setup_logger
from app.modules import router

logger = setup_logger()
settings = get_settings()
app = FastAPI()

app.include_router(router)
