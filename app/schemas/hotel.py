
from pydantic import BaseModel
from typing import List, Optional
from app.schemas.amenity import AmenityOut
from app.schemas.media import MediaOut, MediaIn
from app.schemas.room import RoomOut, RoomIn


# -------------------- SAÍDA --------------------

class HotelCard(BaseModel):
    id: int
    name: str
    city: str
    neighborhood: Optional[str] = None
    stars: float
    popularity: float
    min_price_general: Optional[float] = None
    min_price_available: Optional[float] = None
    distance_km: Optional[float] = None
    thumbnail: Optional[str] = None

    class Config:
        from_attributes = True


class HotelDetail(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    city: str
    neighborhood: Optional[str] = None
    address: Optional[str] = None
    latitude: float
    longitude: float
    stars: float
    popularity: float
    policies: Optional[str] = None

    amenities: List[AmenityOut] = []
    media: List[MediaOut] = []
    rooms: List[RoomOut] = []

    min_price_general: Optional[float] = None
    min_price_available: Optional[float] = None
    distance_km: Optional[float] = None
    thumbnail: Optional[str] = None

    class Config:
        from_attributes = True



# -------------------- ENTRADA --------------------

class HotelIn(BaseModel):
    name: str
    description: Optional[str] = None
    city: str
    neighborhood: Optional[str] = None
    address: Optional[str] = None
    latitude: float
    longitude: float
    stars: float
    popularity: float
    policies: Optional[str] = None

    amenities: List[int] = []

    media: List[MediaIn] = []
    rooms: List[RoomIn] = []

    class Config:
        from_attributes = True

