from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date

class HotelFilter(BaseModel):
    # Filtros básicos
    q: Optional[str] = Field(None, description="Busca textual pelo nome do hotel")
    city: Optional[str] = None
    neighborhood: Optional[str] = None
    amenities: Optional[List[int]] = None
    room_type: Optional[str] = None

    # Filtros de preço
    price_min: Optional[float] = None
    price_max: Optional[float] = None

    # Filtros de período
    check_in: Optional[date] = None
    check_out: Optional[date] = None

    # Ordenação
    sort: Optional[str] = Field("id", description="Critério de ordenação: id, price, rating, popularity, distance")

    # Filtros relacionados a distância
    user_lat: Optional[float] = None
    user_lng: Optional[float] = None

    # Filtros de estrelas
    stars_min: Optional[float] = Field(None, ge=0, le=5)
    stars_max: Optional[float] = Field(None, ge=0, le=5)

    # Paginação
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)

    # ----------------- FIELD VALIDATORS -----------------
    @field_validator("user_lat")
    @classmethod
    def latitude_range(cls, v):
        if v is not None and not (-90 <= v <= 90):
            raise ValueError("user_lat must be between -90 and 90")
        return v

    @field_validator("user_lng")
    @classmethod
    def longitude_range(cls, v):
        if v is not None and not (-180 <= v <= 180):
            raise ValueError("user_lng must be between -180 and 180")
        return v

    @field_validator("sort")
    @classmethod
    def allowed_sort(cls, v):
        allowed = {"id", "price", "rating", "popularity", "distance"}
        if v not in allowed:
            raise ValueError(f"sort must be one of: {', '.join(allowed)}")
        return v
