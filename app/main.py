from fastapi import FastAPI
from app.database.database import test_connection
from app.routers import hotels, users, login, amenity_router

app = FastAPI(title="Aluga API")

# Inclui routers
app.include_router(hotels.router)
app.include_router(users.router)
app.include_router(login.router)
app.include_router(amenity_router.router)

@app.on_event("startup")
def on_startup():
    """
    Evento de inicialização da API:
    - Testa a conexão com o banco
    """
    test_connection()

@app.get("/health")
def healthcheck():
    """
    Endpoint para checar se a API e o banco estão funcionando
    """
    try:
        test_connection()
        return {"status": "ok"}
    except Exception:
        return {"status": "error"}

