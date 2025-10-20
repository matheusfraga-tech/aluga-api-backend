import re
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime
from app.database.database import test_connection
from app.routers import hotels, users, login, amenity_router
import psycopg2
import logging
import time
from fastapi.middleware.cors import CORSMiddleware

# -------------------- Configurações --------------------

# -------------------- CORS --------------------
origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8081",
    "http://127.0.0.1:8081",
    "http://192.168.0.9:8000"
    ]

# Logging estruturado
logger = logging.getLogger("aluga-api")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# -------------------- App --------------------
app = FastAPI(title="Aluga API")

# -------------------- Middleware --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex= '^https:\/\/[a-zA-Z0-9-]+\.mmar\.dev$',
    allow_origins=origins,  # Or use ["*"] for all (not recommended in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- Routers --------------------
app.include_router(hotels.router, tags=["hotels"])
app.include_router(users.router, tags=["users"])
app.include_router(login.router, tags=["auth"])
app.include_router(amenity_router.router, tags=["amenities"])

# -------------------- Eventos de Startup --------------------
@app.on_event("startup")
def on_startup():
    """
    Evento de inicialização da API:
    - Testa a conexão com o banco
    - Loga versão e status
    """
    try:
        conn_info = test_connection()
        logger.info(f"Conectado ao Postgres: {conn_info}")
    except Exception as e:
        logger.error(f"Falha ao conectar ao banco: {e}")

# -------------------- Healthcheck --------------------
@app.get("/health", tags=["Health"])
def healthcheck():
    """
    Healthcheck da API:
    - Status da API
    - Status do banco
    - Latência do banco
    - Mensagens detalhadas
    - Timestamp
    """
    result = {
        "api_status": "ok",
        "db_status": "unknown",
        "details": {},
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    try:
        start_time = time.time()
        conn_info = test_connection()
        latency_ms = round((time.time() - start_time) * 1000, 2)

        result["db_status"] = "ok"
        result["details"]["db_info"] = conn_info
        result["details"]["db_latency_ms"] = latency_ms
    except psycopg2.OperationalError as e:
        result["api_status"] = "degraded"
        result["db_status"] = "error"
        result["details"]["db_error"] = str(e)
    except Exception as e:
        result["api_status"] = "error"
        result["db_status"] = "error"
        result["details"]["exception"] = str(e)

    status_code = 200 if result["db_status"] == "ok" else 503

    logger.info(f"Healthcheck acessado: {datetime.utcnow().isoformat()} - Status: {result['api_status']}")
    return JSONResponse(status_code=status_code, content=result)
