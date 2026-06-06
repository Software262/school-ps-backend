from fastapi import FastAPI

from app.modules import router

app = FastAPI()


app.include_router(router)

@app.get("/")
def root():
    return {"message": "Backend SchoolPS funcionando correctamente"}