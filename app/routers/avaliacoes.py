# app/routers/avaliacoes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
import statistics

# Importando dependências e schemas
from ..dependencies import get_current_user
from ..database.connection import get_db
from ..schemas import avaliacao as avaliacao_schema
from .. import models

router = APIRouter(
    prefix="/avaliacoes",
    tags=["avaliacoes"]
)

@router.post("/", response_model=avaliacao_schema.Avaliacao, status_code=status.HTTP_201_CREATED)
def criar_avaliacao(
    avaliacao_data: avaliacao_schema.AvaliacaoCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    usuario_id = current_user.get("id")
    if not usuario_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

    # LÓGICA DE NEGÓCIO: Verificar se o hotel existe, se o usuário já avaliou, etc.
    # Por simplicidade, vamos direto para a criação.
    
    nova_avaliacao = models.Avaliacao(
        nota=avaliacao_data.nota,
        comentario=avaliacao_data.comentario,
        hotel_id=avaliacao_data.hotelId,
        usuario_id=usuario_id
    )
    
    try:
        db.add(nova_avaliacao)
        db.commit()
        db.refresh(nova_avaliacao)
        return nova_avaliacao
    except IntegrityError: # Caso o hotel_id ou usuario_id não existam
        db.rollback()
        raise HTTPException(status_code=404, detail="Hotel ou usuário não encontrado.")


@router.get("/hotel/{hotel_id}", response_model=List[avaliacao_schema.Avaliacao])
def ler_avaliacoes_do_hotel(hotel_id: int, db: Session = Depends(get_db)):
    avaliacoes = db.query(models.Avaliacao).filter(models.Avaliacao.hotel_id == hotel_id).all()
    return avaliacoes


@router.get("/hotel/{hotel_id}/stats", response_model=avaliacao_schema.HotelStats)
def ler_estatisticas_do_hotel(hotel_id: int, db: Session = Depends(get_db)):
    notas = db.query(models.Avaliacao.nota).filter(models.Avaliacao.hotel_id == hotel_id).all()
    
    # .all() retorna uma lista de tuplas, ex: [(5.0,), (4.0,)]
    # Precisamos extrair o primeiro elemento de cada tupla.
    notas_list = [n[0] for n in notas]
    
    total = len(notas_list)
    if total == 0:
        return avaliacao_schema.HotelStats(notaMedia=0.0, totalAvaliacoes=0)

    media = round(statistics.mean(notas_list), 1)
    
    return avaliacao_schema.HotelStats(notaMedia=media, totalAvaliacoes=total)