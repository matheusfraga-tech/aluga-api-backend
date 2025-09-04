from fastapi import Depends, FastAPI
from .dependencies import *
from .routers import users, login
from .database.test_connection import test_connection

app = FastAPI()

# inclui routers
app.include_router(users.router)
app.include_router(login.router)
@app.on_event("startup")
def startup_event():
    # testa a conexão com o banco quando a API inicia
    test_connection()

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}

@app.get("/hotel")
def getHotel():
    return {
        "name": "Copacabana Palace",
        "address": "Av. Atlântica, 1702, Copacabana, Rio de Janeiro"
    }
