from pydantic import BaseModel, Field, field_validator, Extra
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
    latitude: float = Field(..., description="Latitude in decimal degrees, between -90 and 90.")
    longitude: float = Field(..., description="Longitude in decimal degrees, between -180 and 180.")
    policies: Optional[str] = None

    amenities: List[int] = []
    media: List[MediaIn] = []
    rooms: List[RoomIn] = []

    class Config:
        from_attributes = True
        extra = Extra.forbid  # Rejeita campos desconhecidos no payload

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError("Latitude must be between -90 and 90 degrees.")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError("Longitude must be between -180 and 180 degrees.")
        return v
