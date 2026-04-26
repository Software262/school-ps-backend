from fastapi import FastAPI

from app.modules import router

app = FastAPI()


app.include_router(router)
