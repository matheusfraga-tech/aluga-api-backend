import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

USER_DB = os.getenv("USER_DB")
USER_PASSWORD = os.getenv("USER_PASSWORD")
HOST_DB = os.getenv("HOST_DB")
PORT_DB = os.getenv("PORT_DB")
DB_NAME = os.getenv("DB_NAME", "aluga-api-v3-database")

DATABASE_URL = f"postgresql+psycopg2://{USER_DB}:{USER_PASSWORD}@{HOST_DB}:{PORT_DB}/{DB_NAME}?sslmode=require"
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def test_connection():
    """Função para testar a conexão com o banco"""
    try:
        with engine.connect() as conn:
            version = conn.execute(text("SELECT version();")).scalar()
            print(f"Conectado ao Postgres: {version}")
    except Exception as e:
        print("Erro ao conectar no banco:", e)
        raise

