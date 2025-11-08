from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class BookingCreate(BaseModel):
    hotel_id: int
    room_id: int
    check_in: date
    check_out: date
    rooms_booked: int = Field(default=1, ge=1)

class BookingUpdate(BaseModel):
    hotel_id: Optional[int] = None
    room_id: Optional[int] = None
    check_in: Optional[date] = None
    check_out: Optional[date] = None
    rooms_booked: Optional[int] = Field(default=None, ge=1)

class BookingOut(BaseModel):
    id: int  # ← MUDOU AQUI
    user_id: str
    hotel_id: int
    room_id: int
    check_in: date
    check_out: date
    rooms_booked: int

    class Config:
        from_attributes = True