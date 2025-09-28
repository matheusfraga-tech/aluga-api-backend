import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator

# Carrega variáveis do ambiente local
load_dotenv()

USER_DB = os.getenv("USER_DB")
USER_PASSWORD = os.getenv("USER_PASSWORD")
HOST_DB = os.getenv("HOST_DB")
PORT_DB = os.getenv("PORT_DB")
DB_NAME = os.getenv("DB_NAME")
SSL_MODE = os.getenv("SSL_MODE")

if not all([USER_DB, USER_PASSWORD, HOST_DB, PORT_DB, DB_NAME]):
    raise ValueError("Variáveis de ambiente do banco não estão configuradas corretamente")

DATABASE_URL = (
    f"postgresql+psycopg2://{USER_DB}:{USER_PASSWORD}@{HOST_DB}:{PORT_DB}/{DB_NAME}?sslmode={SSL_MODE}"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection() -> str:
    """
    Testa a conexão com o banco e retorna informações do servidor.
    """
    try:
        with engine.connect() as conn:
            version = conn.execute(text("SELECT version();")).scalar()
            return version  # <-- retorna a versão do Postgres
    except Exception as e:
        raise e

