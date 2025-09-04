from fastapi import FastAPI
from .dependencies import *
from .routers import users, login
# from .database.test_connection import test_connection, engine
# from sqlalchemy import text

app = FastAPI()

# inclui routers
app.include_router(users.router)
app.include_router(login.router)

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}