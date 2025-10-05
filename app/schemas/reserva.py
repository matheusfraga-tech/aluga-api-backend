from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional

# Schema para exibir dados do usuário (dentro da reserva)
class UserOut(BaseModel):
    id: str
    user_name: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    role: Optional[str]

    model_config = ConfigDict(from_attributes=True)


# Schema para criar uma reserva
class ReservationCreate(BaseModel):
    room_id: int
    date_checkin: datetime
    date_checkout: datetime


# Schema para exibir uma reserva
class ReservationOut(BaseModel):
    id: str
    user_id: str
    quarto_id: int = Field(..., alias="room_id")
    data_checkin: datetime = Field(..., alias="date_checkin")
    data_checkout: datetime = Field(..., alias="date_checkout")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

# Schema para update de reserva
class ReservationUpdate(BaseModel):
    date_checkin: Optional[datetime]
    date_checkout: Optional[datetime]
    room_id: Optional[int]