# app/routers/avaliacoes.py
from fastapi import APIRouter, HTTPException, status
from typing import List
import uuid
from datetime import datetime, timezone # Importe datetime e timezone

from .. import dependencies
from ..schemas.avaliacao import Avaliacao, AvaliacaoCreate, UsuarioSimples

router = APIRouter(
    prefix="/avaliacoes",
    tags=["avaliacoes"]
)

@router.post("/", response_model=Avaliacao, status_code=status.HTTP_201_CREATED)
def criar_avaliacao(
    avaliacao_data: AvaliacaoCreate
):
    usuario_id = avaliacao_data.usuarioId
    
    if avaliacao_data.hotelId not in dependencies.fake_hoteis_db:
        raise HTTPException(status_code=404, detail="Hotel não encontrado")
        
    usuario_info = next((user for user in dependencies.fake_users_db.values() if user["id"] == usuario_id), None)
    if not usuario_info:
        raise HTTPException(status_code=404, detail=f"Usuário com id '{usuario_id}' não encontrado")
    
    # Adiciona a data de criação ao dicionário
    nova_avaliacao = {
        "id": str(uuid.uuid4()),
        "nota": avaliacao_data.nota,
        "comentario": avaliacao_data.comentario,
        "hotelId": avaliacao_data.hotelId,
        "usuarioId": usuario_id,
        "dataCriacao": datetime.now(timezone.utc) # Adiciona o timestamp
    }
    
    dependencies.fake_avaliacoes_db.append(nova_avaliacao)
    
    # CORREÇÃO 1: Crie UsuarioSimples apenas com userName
    usuario_schema = UsuarioSimples(userName=usuario_info.get("userName"))
    
    # CORREÇÃO 2: Passe todos os campos esperados pelo schema Avaliacao
    return Avaliacao(
        id=nova_avaliacao["id"],
        nota=nova_avaliacao["nota"],
        comentario=nova_avaliacao["comentario"],
        dataCriacao=nova_avaliacao["dataCriacao"], # <-- Passe a data de criação
        hotelId=nova_avaliacao["hotelId"],         # <-- Agora este campo é esperado
        usuario=usuario_schema
    )

@router.get("/hotel/{hotel_id}", response_model=List[Avaliacao])
def ler_avaliacoes_do_hotel(hotel_id: int):
    if hotel_id not in dependencies.fake_hoteis_db:
        raise HTTPException(status_code=404, detail="Hotel não encontrado")
    
    avaliacoes_do_hotel = [aval for aval in dependencies.fake_avaliacoes_db if aval["hotelId"] == hotel_id]
    
    resposta_formatada = []
    for aval in avaliacoes_do_hotel:
        usuario_info = next((user for user in dependencies.fake_users_db.values() if user["id"] == aval["usuarioId"]), None)
        if usuario_info:
            # CORREÇÃO 1 (aplicada aqui também)
            usuario_schema = UsuarioSimples(userName=usuario_info.get("userName"))

            # Aqui você não está montando o objeto de resposta, mas deveria para garantir consistência.
            # O ideal é que o 'fake_avaliacoes_db' já tivesse o 'dataCriacao'.
            # Por simplicidade, vamos criar uma data fictícia se não existir.
            data_criacao_obj = aval.get("dataCriacao", datetime.now(timezone.utc))

            # CORREÇÃO 2 (aplicada aqui também)
            resposta_formatada.append(Avaliacao(
                id=aval["id"],
                nota=aval["nota"],
                comentario=aval["comentario"],
                dataCriacao=data_criacao_obj, # Passando a data
                hotelId=aval["hotelId"],       # Passando o hotelId
                usuario=usuario_schema
            ))

    return resposta_formatada