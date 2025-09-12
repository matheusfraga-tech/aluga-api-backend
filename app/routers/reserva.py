from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.reserva import ReservaCreate, ReservaResponse

router = APIRouter(
    prefix="/reservas",
    tags=["reservas"]
)

# Banco de dados fake (temporário, só para teste)
reservas_db = []

# POST /reservas/ → cria uma reserva (salva em uma lista na memória)
@router.post("/", response_model=ReservaResponse)
def criar_reserva(reserva: ReservaCreate):
    nova_reserva = ReservaResponse(
        id=len(reservas_db) + 1,
        status="ativo",
        **reserva.dict()
    )
    reservas_db.append(nova_reserva)
    return nova_reserva

# GET /reservas/ → lista todas as reservas já criadas
@router.get("/", response_model=List[ReservaResponse])
def listar_reservas():
    return reservas_db