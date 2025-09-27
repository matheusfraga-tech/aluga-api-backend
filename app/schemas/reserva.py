from pydantic import BaseModel
from datetime import datetime

#Schema para criar uma reserva
class ReservaCreate(BaseModel):
    cliente: str
    data_checkin: datetime
    data_checkout: datetime
    quarto_id: int

#Schema para exibir uma reserva
class ReservaOut(ReservaCreate):
    id: int

    class Config:
        from_attributes = True  #permite converter do modelo SQLAlchemy
