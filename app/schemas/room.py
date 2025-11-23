from pydantic import BaseModel
from typing import List, Optional # Importe Optional se for usar id para update
from app.schemas.amenity import AmenityOut, AmenityIn

# -------------------- SAÍDA --------------------
class RoomOut(BaseModel):
    id: int
    name: str
    room_type: str
    capacity: int
    base_price: float
    total_units: int
    amenities: List[AmenityOut] = []

    class Config:
        from_attributes = True

# -------------------- ENTRADA --------------------
class RoomIn(BaseModel):
    name: str
    room_type: str
    capacity: int
    base_price: float
    total_units: int
    
    amenities: List[int] = [] 

    class Config:
        from_attributes = True