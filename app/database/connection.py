# app/database/connection.py

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

USER_DB = os.getenv("USER_DB")
USER_PASSWORD = os.getenv("USER_PASSWORD")
HOST_DB = os.getenv("HOST_DB")
PORT_DB = os.getenv("PORT_DB", "5432")
DB_NAME = os.getenv("DB_NAME", "aluga-api-v3-database")

DATABASE_URL = f"postgresql+psycopg2://{USER_DB}:{USER_PASSWORD}@{HOST_DB}:{PORT_DB}/{DB_NAME}?sslmode=disable"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Função de dependência para obter a sessão do banco de dados em cada request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()