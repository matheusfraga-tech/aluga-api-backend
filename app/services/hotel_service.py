from math import radians, cos, sin, atan2, sqrt
from typing import List, Optional

from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.models.hotel import Hotel
from app.models.room import Room
from app.models.media import Media
from app.repositories.hotel_repository import HotelRepository
from app.schemas.hotel import HotelIn, HotelDetail, HotelCard
from app.schemas.room import RoomIn
from app.schemas.media import MediaIn
from app.schemas.hotel_filter import HotelFilter


class HotelService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = HotelRepository()

    # -------------------- FUNÇÃO DE HAVERSINE --------------------
    @staticmethod
    def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        Calcula a distância em km entre dois pontos geográficos.
        """
        R = 6371  # Raio da Terra em km
        phi1, phi2 = radians(lat1), radians(lat2)
        delta_phi = radians(lat2 - lat1)
        delta_lambda = radians(lng2 - lng1)

        a = sin(delta_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(delta_lambda / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return R * c

    # -------------------- CRUD --------------------
    def create_hotel(self, hotel_in: HotelIn) -> Hotel:
        """
        Cria um hotel simples, delegando validação de proximidade para o repository.
        """
        hotel = Hotel(
            name=hotel_in.name,
            description=hotel_in.description,
            city=hotel_in.city,
            neighborhood=hotel_in.neighborhood,
            address=hotel_in.address,
            latitude=hotel_in.latitude,
            longitude=hotel_in.longitude,
            policies=hotel_in.policies,
        )
        return self.repo.create(self.db, hotel)


    # -------------------- GET --------------------
    def get_hotel(
        self,
        hotel_id: int,
        user_lat: Optional[float] = None,
        user_lng: Optional[float] = None,
        check_in: Optional[str] = None,
        check_out: Optional[str] = None,
    ) -> Optional[Hotel]:

        # Valida filtros de entrada
        filters = HotelFilter(
            user_lat=user_lat,
            user_lng=user_lng,
            check_in=check_in,
            check_out=check_out
        )
        self.validate_filters(filters)

        # Busca o hotel no repo, já calculando min_price_available se datas forem fornecidas
        hotel = self.repo.get(self.db, hotel_id, check_in=check_in, check_out=check_out)
        if not hotel:
            return None

        # Preço mínimo geral
        hotel.min_price_general = self.calculate_min_price_general(hotel)

        # Distância e thumbnail
        hotel.distance_km = (
            self._calculate_distance(hotel, user_lat, user_lng)
            if user_lat is not None and user_lng is not None else None
        )
        hotel.thumbnail = self._get_thumbnail(hotel)

        return hotel



    def update_hotel(self, hotel_id: int, hotel_in: HotelIn) -> Optional[Hotel]:
        return self.repo.update(self.db, hotel_id, hotel_in)

    def delete_hotel(self, hotel_id: int) -> bool:
        return self.repo.delete(self.db, hotel_id)

    def get_all_hotels(self) -> List[HotelCard]:
        """
        Retorna todos os hotéis cadastrados.
        """
        empty_filters = HotelFilter()

        page_result = self.repo.search(self.db, empty_filters)
        
        hotels = [item for item in page_result.items] 
        
        return hotels

    def create_full(self, hotel_in: HotelIn) -> Hotel:
        """
        Cria hotel completo (com quartos, mídias e comodidades), delegando validação para o repository.
        """
        return self.repo.create_full(self.db, hotel_in)

    # -------------------- ORCHESTRADORES --------------------
    def add_rooms(self, hotel_id: int, rooms_in: List[RoomIn]) -> Hotel:
        return self.repo.add_rooms(self.db, hotel_id, rooms_in)

    def add_media(self, hotel_id: int, media_in: List[MediaIn]) -> Hotel:
        return self.repo.add_media(self.db, hotel_id, media_in)

    def add_amenities(self, hotel_id: int, amenity_ids: List[int]) -> Hotel:
        return self.repo.add_amenities(self.db, hotel_id, amenity_ids)

    # -------------------- MÉTODOS PRIVADOS --------------------
    def _calculate_distance(
        self,
        hotel: Hotel,
        user_lat: Optional[float],
        user_lng: Optional[float]
    ) -> Optional[float]:
        if user_lat is not None and user_lng is not None:
            return self.haversine(user_lat, user_lng, hotel.latitude, hotel.longitude)
        return None

    def _get_thumbnail(self, hotel: Hotel) -> Optional[str]:
        if hotel.media:
            images = [m for m in hotel.media if m.type == "image"]
            return images[0].url if images else None
        return None

    @staticmethod
    def calculate_min_price_general(hotel: Hotel) -> Optional[float]:
        if hotel.rooms:
            available_prices = [room.base_price for room in hotel.rooms if room.total_units > 0]
            return min(available_prices) if available_prices else None
        return None

    @staticmethod
    def validate_filters(filters: HotelFilter):
        errors = []

        # Datas
        if filters.check_in and filters.check_out and filters.check_out <= filters.check_in:
            errors.append({
                "loc": ["query", "check_out"],
                "msg": "check_out must be after check_in",
                "type": "value_error",
                "input": {
                    "check_in": filters.check_in.isoformat(),
                    "check_out": filters.check_out.isoformat()
                }
            })

        # Estrelas
        if filters.stars_min is not None and filters.stars_max is not None and filters.stars_max < filters.stars_min:
            errors.append({
                "loc": ["query", "stars_max"],
                "msg": "stars_max must be greater than or equal to stars_min",
                "type": "value_error",
                "input": {"stars_min": filters.stars_min, "stars_max": filters.stars_max}
            })

        # Distância
        if filters.sort == "distance" and (filters.user_lat is None or filters.user_lng is None):
            errors.append({
                "loc": ["query", "user_lat/user_lng"],
                "msg": "For distance sorting, user_lat and user_lng must be provided",
                "type": "value_error",
                "input": {"user_lat": filters.user_lat, "user_lng": filters.user_lng}
            })

        if errors:
            raise HTTPException(status_code=422, detail=errors)



    # -------------------- SEARCH --------------------
    def search(
        self,
        filters: HotelFilter,
        user_lat: Optional[float] = None,
        user_lng: Optional[float] = None
    ) -> List[Hotel]:
        """
        Busca hotéis usando o repository e calcula distância e thumbnail.
        """
        # Valida consistência de negócio
        self.validate_filters(filters)

        # Usa o search do repository
        page_result = self.repo.search(self.db, filters)

        hotels = [item for item in page_result.items]  # lista de Hotel ou HotelCard

        # Calcula distância se coordenadas do usuário forem fornecidas
        if user_lat is not None and user_lng is not None:
            for h in hotels:
                h.distance_km = self._calculate_distance(h, user_lat, user_lng)
        else:
            for h in hotels:
                h.distance_km = None


        return hotels

