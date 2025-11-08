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

# Schema básico (sem relacionamentos)
class BookingOut(BaseModel):
    id: int
    user_id: str
    hotel_id: int
    room_id: int
    check_in: date
    check_out: date
    rooms_booked: int

    class Config:
        from_attributes = True

# Schemas para dados aninhados
class HotelNested(BaseModel):
    id: int
    name: str
    city: str
    stars: float
    
    class Config:
        from_attributes = True

class RoomNested(BaseModel):
    id: int
    name: str
    room_type: str
    base_price: float
    
    class Config:
        from_attributes = True

# Schema completo com relacionamentos
class BookingWithDetails(BaseModel):
    id: int
    user_id: str
    hotel_id: int
    room_id: int
    check_in: date
    check_out: date
    rooms_booked: int
    hotel: HotelNested
    room: RoomNested

    class Config:
        from_attributes = True