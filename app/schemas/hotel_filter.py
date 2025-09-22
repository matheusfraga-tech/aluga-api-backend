from pydantic import BaseModel, Field, root_validator
from typing import Optional, List
from datetime import date

class HotelFilter(BaseModel):
    # Filtros básicos
    q: Optional[str] = Field(None, description="Busca textual pelo nome do hotel")
    city: Optional[str] = None
    neighborhood: Optional[str] = None
    amenities: Optional[List[int]] = Field(None, description="IDs das amenities")
    room_type: Optional[str] = None

    # Filtros de preço
    price_min: Optional[float] = Field(None, description="Preço mínimo (usa min_price_available se datas informadas)")
    price_max: Optional[float] = Field(None, description="Preço máximo (usa min_price_available se datas informadas)")

    # Filtros de período
    check_in: Optional[date] = Field(None, description="Data de check-in")
    check_out: Optional[date] = Field(None, description="Data de check-out")

    # Ordenação
    sort: Optional[str] = Field(
        "id",
        description="Critério de ordenação: id, price, rating, popularity, distance"
    )

    # Filtros relacionados a distância
    user_lat: Optional[float] = Field(None, description="Latitude do ponto de referência para ordenação por distância")
    user_lng: Optional[float] = Field(None, description="Longitude do ponto de referência para ordenação por distância")

    # Filtros de stars
    stars_min: Optional[float] = Field(None, ge=0, le=5, description="Nota mínima do hotel (0-5)")
    stars_max: Optional[float] = Field(None, ge=0, le=5, description="Nota máxima do hotel (0-5)")

    # Paginação
    page: int = Field(1, ge=1, description="Número da página")
    size: int = Field(20, ge=1, le=100, description="Tamanho da página")

    @root_validator
    def validate_filters(cls, values):
        sort = values.get("sort")
        lat = values.get("user_lat")
        lng = values.get("user_lng")
        check_in = values.get("check_in")
        check_out = values.get("check_out")
        stars_min = values.get("stars_min")
        stars_max = values.get("stars_max")

        # Validação de distância
        if sort == "distance" and (lat is None or lng is None):
            raise ValueError("Para ordenação por distância, user_lat e user_lng devem ser fornecidos")

        # Validação de datas
        if check_in and check_out and check_out <= check_in:
            raise ValueError("check_out deve ser posterior a check_in")

        # Validação de stars
        if stars_min is not None and stars_max is not None and stars_max < stars_min:
            raise ValueError("stars_max deve ser maior ou igual a stars_min")

        # Validação de sort
        allowed_sort = {"id", "price", "rating", "popularity", "distance"}
        if sort not in allowed_sort:
            raise ValueError(f"sort deve ser um dos: {', '.join(allowed_sort)}")

        return values

