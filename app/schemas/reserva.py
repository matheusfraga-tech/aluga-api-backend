from pydantic import BaseModel
from datetime import datetime

# Schema para criar uma reserva
class ReservationCreate(BaseModel):
    #user_id: str           # vincula a reserva ao usuário
    room_id: int           # vincula a reserva ao quarto
    date_checkin: datetime
    date_checkout: datetime

# Schema para exibir uma reserva
class ReservationOut(ReservationCreate):
    id: str 

    class Config:
        from_attributes = True 
