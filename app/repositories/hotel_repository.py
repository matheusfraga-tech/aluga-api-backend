from sqlalchemy.orm import Session
from sqlalchemy import func, select
from sqlalchemy.sql import label
from app.models.hotel import Hotel
from app.models.room import Room
from app.models.media import Media
from app.models.amenity import Amenity
from app.schemas.hotel import HotelIn
from app.schemas.room import RoomIn
from app.schemas.media import MediaIn
from app.schemas.hotel_filter import HotelFilter
from app.schemas.pagination import Page

import math

class HotelRepository:

    # -------------------- CREATE --------------------
    def create(self, db: Session, hotel: Hotel) -> Hotel:
        db.add(hotel)
        db.commit()
        db.refresh(hotel)
        return hotel

    # -------------------- READ --------------------
    def get(self, db: Session, hotel_id: int) -> Hotel | None:
        return db.get(Hotel, hotel_id)

    def list(self, db: Session) -> list[Hotel]:
        return db.query(Hotel).all()

    # -------------------- UPDATE --------------------
    def update(self, db: Session, hotel_id: int, hotel_in: HotelIn) -> Hotel | None:
        hotel = db.get(Hotel, hotel_id)
        if not hotel:
            return None
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
    def add_rooms(self, db: Session, hotel_id: int, rooms_in: list[RoomIn]) -> Hotel:
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
    def add_media(self, db: Session, hotel_id: int, media_in: list[MediaIn]) -> Hotel:
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
    def add_amenities(self, db: Session, hotel_id: int, amenity_ids: list[int]) -> Hotel:
        hotel = db.get(Hotel, hotel_id)
        if not hotel:
            raise ValueError("Hotel not found")
        amenities = db.query(Amenity).filter(Amenity.id.in_(amenity_ids)).all()
        hotel.amenities.extend(amenities)
        db.commit()
        db.refresh(hotel)
        return hotel


def search(self, db: Session, filters: HotelFilter) -> Page[HotelCard]:
    from sqlalchemy.orm import aliased
    from sqlalchemy import case

    # -------------------- Subquery de quartos disponíveis --------------------
    booked_subq = (
        db.query(
            Booking.room_id.label("room_id"),
            func.coalesce(func.sum(Booking.rooms_booked), 0).label("rooms_booked")
        )
        .filter(
            Booking.check_in < filters.check_out,
            Booking.check_out > filters.check_in
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

    # -------------------- Query base --------------------
    query = (
        db.query(
            Hotel,
            room_avail_subq.c.min_price
        )
        .outerjoin(room_avail_subq, Hotel.id == room_avail_subq.c.hotel_id)
        .options(joinedload(Hotel.media))
    )

    # -------------------- Filtros --------------------
    if filters.q:
        query = query.filter(Hotel.name.ilike(f"%{filters.q}%"))
    if filters.city:
        query = query.filter(Hotel.city.ilike(f"%{filters.city}%"))
    if filters.neighborhood:
        query = query.filter(Hotel.neighborhood.ilike(f"%{filters.neighborhood}%"))

    # -------------------- Ordenação --------------------
    if filters.sort == "price":
        query = query.order_by(room_avail_subq.c.min_price.asc().nullslast())
    elif filters.sort == "popularity":
        query = query.order_by(Hotel.popularity.desc())
    elif filters.sort == "stars":
        query = query.order_by(Hotel.stars.desc())
    else:
        query = query.order_by(Hotel.id.asc())

    # -------------------- Paginação --------------------
    total = query.count()
    hotels = query.offset((filters.page - 1) * filters.size).limit(filters.size).all()

    # -------------------- Construção dos itens --------------------
    items = []
    for hotel, min_price in hotels:
        # thumbnail
        thumbnail = hotel.media[0].url if hotel.media else None

        # distance_km
        if filters.user_lat is not None and filters.user_lng is not None:
            distance_km = haversine(filters.user_lat, filters.user_lng, hotel.latitude, hotel.longitude)
        else:
            distance_km = None

        items.append(HotelCard(
            id=hotel.id,
            name=hotel.name,
            city=hotel.city,
            neighborhood=hotel.neighborhood,
            stars=hotel.stars,
            popularity=hotel.popularity,
            min_price=min_price,
            distance_km=distance_km,
            thumbnail=thumbnail
        ))

    # -------------------- Ordenação por distância --------------------
    if filters.sort == "distance" and filters.user_lat is not None and filters.user_lng is not None:
        items.sort(key=lambda x: (x.distance_km if x.distance_km is not None else float('inf')))

    return Page[HotelCard](
        meta=PageMeta(page=filters.page, size=filters.size, total=total),
        items=items
    )


def haversine(lat1, lon1, lat2, lon2):
    """Calcula distância em km entre dois pontos"""
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6371 * c
    return km
