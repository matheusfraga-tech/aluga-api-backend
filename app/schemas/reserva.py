from pydantic import BaseModel
from datetime import date

# Campos básicos da reserva
class ReservaBase(BaseModel):
    usuario_id: int
    quarto_id: int
    data_checkin: date
    data_checkout: date

# Usado quando o usuário cria uma nova reserva
class ReservaCreate(ReservaBase):
    pass

# Resposta da API
class ReservaResponse(ReservaBase):
    id: int
    status: str

    class Config:
        orm_mode = True