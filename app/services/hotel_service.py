from sqlalchemy.orm import Session
from typing import List, Optional
import math
from app.repositories.hotel_repository import HotelRepository
from app.schemas.hotel import HotelIn
from app.models.hotel import Hotel
from app.models.room import Room
from app.models.media import Media


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
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lng2 - lng1)

        a = math.sin(delta_phi / 2) ** 2 + \
            math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    # -------------------- CRUD --------------------
    def create_hotel(self, hotel_in: HotelIn) -> Hotel:
        hotel = Hotel(
            name=hotel_in.name,
            description=hotel_in.description,
            city=hotel_in.city,
            neighborhood=hotel_in.neighborhood,
            address=hotel_in.address,
            latitude=hotel_in.latitude,
            longitude=hotel_in.longitude,
            stars=hotel_in.stars,
            popularity=hotel_in.popularity,
            policies=hotel_in.policies,
        )
        return self.repo.create(self.db, hotel)

	def get_hotel(
	    self,
	    hotel_id: int,
	    user_lat: Optional[float] = None,
	    user_lng: Optional[float] = None
	) -> Optional[Hotel]:
	    """
	    Retorna todos os detalhes de um hotel, incluindo:
	    - amenities
	    - rooms
	    - media
	    - bookings
	    - reviews
	    Calcula:
	    - min_price_general (sempre)
	    - min_price_available (None, pois não há período definido)
	    - distance_km (se coordenadas fornecidas)
	    - thumbnail
	    """
	    hotel = self.repo.get(self.db, hotel_id)
	    if not hotel:
	        return None
	
	    # -------------------- PREÇOS --------------------
	    hotel.min_price_general = self.calculate_min_price_general(hotel)

        #TODO: implementar consulta com check_in e check_out como filtros para o get_hotel.
	    hotel.min_price_available = None  # fallback, sem período definido
	
	    # -------------------- DISTÂNCIA --------------------
	    if user_lat is not None and user_lng is not None:
	        hotel.distance_km = self._calculate_distance(hotel, user_lat, user_lng)
	    else:
	        hotel.distance_km = None
	
	    # -------------------- THUMBNAIL --------------------
	    hotel.thumbnail = self._get_thumbnail(hotel)
	
	    return hotel


    def update_hotel(self, hotel_id: int, hotel_in: HotelIn) -> Optional[Hotel]:
        return self.repo.update(self.db, hotel_id, hotel_in)

    def delete_hotel(self, hotel_id: int) -> bool:
        return self.repo.delete(self.db, hotel_id)

    # -------------------- CREATE FULL --------------------
    def create_full(self, hotel_in: HotelIn) -> Hotel:
        return self.repo.create_full(self.db, hotel_in)

    # -------------------- CREATE ORCHESTRADO --------------------
    def add_rooms(self, hotel_id: int, rooms_in: List[RoomIn]) -> Hotel:
        return self.repo.add_rooms(self.db, hotel_id, rooms_in)

    def add_media(self, hotel_id: int, media_in: List[MediaIn]) -> Hotel:
        return self.repo.add_media(self.db, hotel_id, media_in)

    def add_amenities(self, hotel_id: int, amenity_ids: List[int]) -> Hotel:
        return self.repo.add_amenities(self.db, hotel_id, amenity_ids)

    # -------------------- MÉTODOS PRIVADOS --------------------
    def _calculate_min_price(self, hotel: Hotel) -> Optional[float]:
        if hotel.rooms:
            available_prices = [room.base_price for room in hotel.rooms if room.total_units > 0]
            return min(available_prices) if available_prices else None
        return None

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
    def calculate_min_price_available(
        hotel: Hotel,
        check_in: Optional[str],
        check_out: Optional[str],
        is_room_available_func=None
    ) -> Optional[float]:
        if check_in and check_out and is_room_available_func:
            available_rooms = [
                r for r in hotel.rooms
                if r.total_units > 0 and is_room_available_func(r, check_in, check_out)
            ]
            return min([r.base_price for r in available_rooms], default=None)
        return None


	def search(
	    self,
	    filters: HotelFilter,
	    user_lat: Optional[float] = None,
	    user_lng: Optional[float] = None
	) -> List[Hotel]:
	    """
	    Busca hotéis com filtros e ordenação de acordo com as regras de negócio.
	    """
	
	    # -------------------- 1 - Lista inicial de hotéis --------------------
	    hotels = self.repo.list(self.db)  # ou query base do repo
	
	    # -------------------- 2 - Filtrar por nome, cidade e bairro --------------------
	    if filters.q:
	        hotels = [h for h in hotels if filters.q.lower() in h.name.lower()]
	
	    if filters.city:
	        hotels = [h for h in hotels if filters.city.lower() in h.city.lower()]
	
	    if filters.neighborhood:
	        hotels = [h for h in hotels if h.neighborhood and filters.neighborhood.lower() in h.neighborhood.lower()]
	
	    # -------------------- 3 - Filtrar por amenities --------------------
	    if filters.amenities:
	        hotels = [
	            h for h in hotels
	            if all(a_id in [a.id for a in h.amenities] for a_id in filters.amenities)
	        ]
	
	    # -------------------- 4 - Filtrar por room_type --------------------
	    if filters.room_type:
	        hotels = [
	            h for h in hotels
	            if any(room.room_type == filters.room_type for room in h.rooms)
	        ]
	
	    # -------------------- 5 - Filtrar por período e preço --------------------
	    check_in, check_out = filters.check_in, filters.check_out
	    price_min, price_max = filters.price_min, filters.price_max
	
	    for h in hotels:
	        # Preço histórico (geral)
	        h.min_price_general = self._calculate_min_price(h)
	
	        # Preço disponível no período
	        if check_in and check_out:
	            available_rooms = [
	                r for r in h.rooms
	                if r.total_units > 0 and self.repo.is_room_available(r, check_in, check_out)
	            ]
	            h.min_price_available = min([r.base_price for r in available_rooms], default=None)
	        else:
	            h.min_price_available = None  # sem datas, não podemos garantir disponibilidade real
	
	    # Aplicar filtros de faixa de preço
	    if price_min is not None:
	        hotels = [
	            h for h in hotels
	            if (h.min_price_available if h.min_price_available is not None else h.min_price_general) >= price_min
	        ]
	
	    if price_max is not None:
	        hotels = [
	            h for h in hotels
	            if (h.min_price_available if h.min_price_available is not None else h.min_price_general) <= price_max
	        ]
	
	    # -------------------- 6 - Filtrar por stars --------------------
	    if filters.stars_min is not None:
	        hotels = [h for h in hotels if h.stars >= filters.stars_min]
	
	    if filters.stars_max is not None:
	        hotels = [h for h in hotels if h.stars <= filters.stars_max]
	
	    # -------------------- 7 - Calcular distância se coordenadas fornecidas --------------------
	    if user_lat is not None and user_lng is not None:
	        for h in hotels:
	            h.distance_km = self._calculate_distance(h, user_lat, user_lng)
	    else:
	        for h in hotels:
	            h.distance_km = None
	
		# -------------------- 8 - Ordenação exclusiva --------------------
		if filters.sort:
		    if filters.sort == "price":
		        hotels.sort(
		            key=lambda h: h.min_price_available
		            if h.min_price_available is not None
		            else (h.min_price_general if h.min_price_general is not None else float('inf'))
		        )
		    elif filters.sort == "distance" and user_lat is not None and user_lng is not None:
		        hotels.sort(
		            key=lambda h: h.distance_km
		            if h.distance_km is not None
		            else float('inf')
		        )
		    elif filters.sort == "stars":
		        hotels.sort(key=lambda h: h.stars, reverse=True)
		    elif filters.sort == "popularity":
		        hotels.sort(key=lambda h: h.popularity, reverse=True)

	
	    # -------------------- 9 - Definir thumbnail --------------------
	    for h in hotels:
	        h.thumbnail = self._get_thumbnail(h)
	
	    return hotels

