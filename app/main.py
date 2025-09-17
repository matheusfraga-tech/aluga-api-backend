from fastapi import FastAPI
from .dependencies import *
from .routers import users, login, avaliacoes
from .database.test_connection import test_connection, engine
from sqlalchemy import text

app = FastAPI()

# inclui routers
app.include_router(users.router)
app.include_router(login.router)
app.include_router(avaliacoes.router)

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

@app.get("/test-db")
def test_db():
    try:
        with engine.connect() as conn:
            version = conn.execute(text("SELECT version();")).scalar()
            return {"status": "ok", "postgres_version": version}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
