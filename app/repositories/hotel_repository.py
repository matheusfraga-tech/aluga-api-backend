from math import radians, cos, sin, asin, sqrt
from typing import List, Optional

from fastapi import HTTPException

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.hotel import Hotel
from app.models.room import Room
from app.models.media import Media
from app.models.amenity import Amenity
from app.schemas.hotel import HotelIn, HotelCard
from app.schemas.room import RoomIn
from app.schemas.media import MediaIn
from app.schemas.hotel_filter import HotelFilter
from app.schemas.pagination import Page, PageMeta
from app.models.booking import Booking
from app.settings import HotelSettings


class HotelRepository:

    # -------------------- GET --------------------
    def get(
        self,
        db: Session,
        hotel_id: int,
        check_in: Optional[str] = None,
        check_out: Optional[str] = None
    ) -> Optional[Hotel]:
        """
        Retorna um hotel completo pelo ID, incluindo:
        - rooms
        - media
        - amenities
        - min_price_general
        - min_price_available (se check_in e check_out forem fornecidos)
        """
        # Query base
        query = db.query(Hotel).options(
            joinedload(Hotel.rooms),
            joinedload(Hotel.media),
            joinedload(Hotel.amenities)
        ).filter(Hotel.id == hotel_id)

        # Subquery de preço mínimo disponível
        min_price_available = None
        if check_in and check_out:
            room_avail_subq = self._min_price_subquery(db, check_in, check_out)
            query = query.add_columns(room_avail_subq.c.min_price).outerjoin(
                room_avail_subq, Hotel.id == room_avail_subq.c.hotel_id
            )

        result = query.first()
        if not result:
            return None

        # Desempacota se subquery foi usada
        hotel, min_price_available = (result if check_in and check_out else (result, None))

        # Define min_price_available
        hotel.min_price_available = min_price_available

        # Calcula min_price_general usando o método estático
        hotel.min_price_general = self.calculate_min_price_general(hotel)

        # Define thumbnail (opcional)
        hotel.thumbnail = hotel.media[0].url if hotel.media else None

        return hotel

    # -------------------- CREATE --------------------
    def create(self, db: Session, hotel: Hotel) -> Hotel:
        self._validate_proximity(db, hotel.latitude, hotel.longitude, hotel.city)
        db.add(hotel)
        db.commit()
        db.refresh(hotel)
        return hotel

    # -------------------- CREATE FULL --------------------
    def create_full(self, db: Session, hotel_in: HotelIn) -> Hotel:
        """
        Cria um hotel completo, incluindo:
        - quartos (rooms)
        - mídias (media)
        - comodidades (amenities)
        """
        # Valida proximidade de hotéis na mesma cidade
        self._validate_proximity(db, hotel_in.latitude, hotel_in.longitude, hotel_in.city)

        # Cria o hotel
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
        db.add(hotel)
        db.commit()
        db.refresh(hotel)

        # -------------------- Rooms --------------------
        for r in hotel_in.rooms:
            room = Room(
                hotel_id=hotel.id,
                name=r.name,
                room_type=r.room_type,
                capacity=r.capacity,
                base_price=r.base_price,
                total_units=r.total_units
            )
            db.add(room)

        # -------------------- Media --------------------
        for m in hotel_in.media:
            media = Media(
                hotel_id=hotel.id,
                url=m.url,
                kind=m.kind or "default"
            )
            db.add(media)

        # -------------------- Amenities --------------------
        if hotel_in.amenities:
            amenities = db.query(Amenity).filter(Amenity.id.in_(hotel_in.amenities)).all()
            hotel.amenities.extend(amenities)

        db.commit()
        db.refresh(hotel)

        return hotel


    # -------------------- UPDATE --------------------
    def update(self, db: Session, hotel_id: int, hotel_in: HotelIn) -> Optional[Hotel]:
        hotel = db.get(Hotel, hotel_id)
        if not hotel:
            return None

        # Se latitude, longitude ou cidade forem alteradas, valida proximidade
        if any(getattr(hotel_in, field) is not None for field in ("latitude", "longitude", "city")):
            lat = hotel_in.latitude if hotel_in.latitude is not None else hotel.latitude
            lng = hotel_in.longitude if hotel_in.longitude is not None else hotel.longitude
            city = hotel_in.city if hotel_in.city is not None else hotel.city
            self._validate_proximity(db, lat, lng, city, exclude_id=hotel_id)

        for field, value in hotel_in.dict(exclude_unset=True).items():
            setattr(hotel, field, value)

        db.commit()
        db.refresh(hotel)
        return hotel

    # -------------------- DELETE --------------------
    def delete(self, db: Session, hotel_id: int) -> bool:
        hotel = db.get(Hotel, hotel_id)
        if not hotel:
            return False
        db.delete(hotel)
        db.commit()
        return True

    # -------------------- ROOMS --------------------
    def add_rooms(self, db: Session, hotel_id: int, rooms_in: List[RoomIn]) -> Hotel:
        hotel = db.get(Hotel, hotel_id)
        if not hotel:
            raise ValueError("Hotel not found")
        for r in rooms_in:
            hotel.rooms.append(Room(
                name=r.name,
                room_type=r.room_type,
                capacity=r.capacity,
                base_price=r.base_price,
                total_units=r.total_units,
            ))
        db.commit()
        db.refresh(hotel)
        return hotel

    # -------------------- MEDIA --------------------
    def add_media(self, db: Session, hotel_id: int, media_in: List[MediaIn]) -> Hotel:
        hotel = db.get(Hotel, hotel_id)
        if not hotel:
            raise ValueError("Hotel not found")
        for m in media_in:
            hotel.media.append(Media(
                url=m.url,
                kind=m.kind or "default"
            ))
        db.commit()
        db.refresh(hotel)
        return hotel

    # -------------------- AMENITIES --------------------
    def add_amenities(self, db: Session, hotel_id: int, amenity_ids: List[int]) -> Hotel:
        hotel = db.get(Hotel, hotel_id)
        if not hotel:
            raise ValueError("Hotel not found")
        amenities = db.query(Amenity).filter(Amenity.id.in_(amenity_ids)).all()
        hotel.amenities.extend(amenities)
        db.commit()
        db.refresh(hotel)
        return hotel

    # -------------------- SEARCH --------------------
    def search(self, db: Session, filters: HotelFilter) -> Page[HotelCard]:
        # Subquery de preço mínimo disponível, se datas forem fornecidas
        room_avail_subq = None
        if filters.check_in and filters.check_out:
            room_avail_subq = self._min_price_subquery(db, filters.check_in, filters.check_out)

        # Query principal
        query = db.query(Hotel)
        if room_avail_subq:
            query = query.add_columns(room_avail_subq.c.min_price).outerjoin(
                room_avail_subq, Hotel.id == room_avail_subq.c.hotel_id
            )

        query = query.options(joinedload(Hotel.media), joinedload(Hotel.rooms))

        # Filtros de texto e localização
        if filters.q:
            query = query.filter(Hotel.name.ilike(f"%{filters.q}%"))
        if filters.city:
            query = query.filter(Hotel.city.ilike(f"%{filters.city}%"))
        if filters.neighborhood:
            query = query.filter(Hotel.neighborhood.ilike(f"%{filters.neighborhood}%"))

        # Ordenação
        if filters.sort == "price" and room_avail_subq:
            query = query.order_by(room_avail_subq.c.min_price.asc().nullslast())
        elif filters.sort == "popularity":
            query = query.order_by(Hotel.popularity.desc())
        elif filters.sort == "stars":
            query = query.order_by(Hotel.stars.desc())
        else:
            query = query.order_by(Hotel.id.asc())

        total = query.count()
        hotels = query.offset((filters.page - 1) * filters.size).limit(filters.size).all()

        items = []
        for result in hotels:
            hotel, min_price_available = (result if room_avail_subq else (result, None))
            min_price_general = self.calculate_min_price_general(hotel)

            thumbnail = hotel.media[0].url if hotel.media else None
            distance_km = None
            if filters.user_lat is not None and filters.user_lng is not None:
                distance_km = HotelRepository.haversine(
                    filters.user_lat, filters.user_lng, hotel.latitude, hotel.longitude
                )

            items.append(HotelCard(
                id=hotel.id,
                name=hotel.name,
                city=hotel.city,
                neighborhood=hotel.neighborhood,
                stars=hotel.stars,
                popularity=hotel.popularity,
                min_price=min_price_available,
                min_price_general=min_price_general,
                distance_km=distance_km,
                thumbnail=thumbnail
            ))

        # Ordenação por distância, feita em Python
        if filters.sort == "distance" and filters.user_lat is not None and filters.user_lng is not None:
            items.sort(key=lambda x: (x.distance_km if x.distance_km is not None else float('inf')))

        return Page[HotelCard](
            meta=PageMeta(page=filters.page, size=filters.size, total=total),
            items=items
        )

    def _validate_proximity(self, db: Session, lat: float, lng: float, city: str, exclude_id: Optional[int] = None):
        radius_meters = HotelSettings.PROXIMITY_RADIUS_METERS
        delta_deg = radius_meters / 111000

        candidates = db.query(Hotel).filter(
            Hotel.city == city,
            Hotel.latitude.between(lat - delta_deg, lat + delta_deg),
            Hotel.longitude.between(lng - delta_deg, lng + delta_deg)
        ).all()

        if exclude_id:
            candidates = [h for h in candidates if h.id != exclude_id]

        nearby_hotels = [
            h for h in candidates
            if HotelRepository.haversine(lat, lng, h.latitude, h.longitude) * 1000 <= radius_meters
        ]

        if nearby_hotels:
            # Aqui substituímos o ValueError por HTTPException
            raise HTTPException(
                status_code=422,
                detail=[{
                    "loc": ["body", "latitude/longitude"],
                    "msg": f"There is already a hotel very close to this address "
                        f"(approximately {radius_meters} meters). Please verify the address or choose another location.",
                    "type": "value_error.proximity",
                    "existing_hotels": [{"id": h.id, "name": h.name} for h in nearby_hotels]
                }]
            )

    @staticmethod
    def haversine(lat1, lon1, lat2, lon2) -> float:
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        km = 6371 * c
        return km

    # -------------------- PRIVATE --------------------
    def _min_price_subquery(self, db: Session, check_in: str, check_out: str):
        """
        Retorna subquery com min_price disponível por hotel, considerando reservas no período informado.
        """
        booked_subq = (
            db.query(
                Booking.room_id.label("room_id"),
                func.coalesce(func.sum(Booking.rooms_booked), 0).label("rooms_booked")
            )
            .filter(
                Booking.check_in < check_out,
                Booking.check_out > check_in
            )
            .group_by(Booking.room_id)
            .subquery()
        )

        room_avail_subq = (
            db.query(
                Room.hotel_id.label("hotel_id"),
                func.min(Room.base_price).label("min_price")
            )
            .outerjoin(booked_subq, Room.id == booked_subq.c.room_id)
            .filter((Room.total_units - func.coalesce(booked_subq.c.rooms_booked, 0)) > 0)
            .group_by(Room.hotel_id)
            .subquery()
        )

        return room_avail_subq

    @staticmethod
    def calculate_min_price_general(hotel: Hotel) -> Optional[float]:
        if hotel.rooms:
            prices = [room.base_price for room in hotel.rooms if room.total_units > 0]
            return min(prices) if prices else None
        return None
