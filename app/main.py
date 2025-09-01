from fastapi import Depends, FastAPI

from .dependencies import *
from .routers import users

app = FastAPI()

app.include_router(users.router)
# app.include_router(
#     admin.router,
#     prefix="/admin",
#     tags=["admin"],
#     dependencies=[Depends(get_token_header)],
#     responses={418: {"description": "I'm a teapot"}},
# )

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}