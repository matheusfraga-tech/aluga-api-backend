from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.services.hotel_service import HotelService
from app.schemas.hotel import HotelIn, HotelDetail, Page
from app.schemas.room import RoomIn
from app.schemas.media import MediaIn
from app.schemas.hotel_filter import HotelFilter

router = APIRouter(prefix="/hotels", tags=["hotels"])

# -------------------- LIST HOTELS --------------------
@router.get("/", response_model=Page[HotelDetail])
def list_hotels(filter: HotelFilter = Depends(), db: Session = Depends(get_db)):
    """
    Lista hotéis com filtros, ordenação e paginação.
    """
    service = HotelService(db)
    return service.list_hotels(filter)

# -------------------- GET HOTEL DETAIL --------------------
@router.get("/{hotel_id}", response_model=HotelDetail)
def get_hotel(hotel_id: int, db: Session = Depends(get_db)):
    """
    Retorna detalhes completos de um hotel.
    """
    service = HotelService(db)
    hotel = service.get_hotel(hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return hotel

# -------------------- CREATE HOTEL --------------------
@router.post("/", response_model=HotelDetail)
def create_hotel(hotel_in: HotelIn, db: Session = Depends(get_db)):
    """
    Cria um hotel simples (sem rooms, media ou amenities).
    """
    service = HotelService(db)
    return service.create_hotel(hotel_in)

# -------------------- UPDATE HOTEL --------------------
@router.put("/{hotel_id}", response_model=HotelDetail)
def update_hotel(hotel_id: int, hotel_in: HotelIn, db: Session = Depends(get_db)):
    """
    Atualiza dados de um hotel existente.
    """
    service = HotelService(db)
    hotel = service.update_hotel(hotel_id, hotel_in)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return hotel

# -------------------- DELETE HOTEL --------------------
@router.delete("/{hotel_id}", status_code=204)
def delete_hotel(hotel_id: int, db: Session = Depends(get_db)):
    """
    Remove um hotel.
    """
    service = HotelService(db)
    deleted = service.delete_hotel(hotel_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return

# -------------------- CREATE FULL HOTEL --------------------
@router.post("/full", response_model=HotelDetail)
def create_full_hotel(hotel_in: HotelIn, db: Session = Depends(get_db)):
    """
    Cria o hotel junto com rooms, media e amenities em um único payload.
    """
    service = HotelService(db)
    return service.create_full_hotel(hotel_in)

# -------------------- ORQUESTRATED ENDPOINTS --------------------
@router.post("/{hotel_id}/rooms", response_model=HotelDetail)
def add_rooms(hotel_id: int, rooms_in: List[RoomIn], db: Session = Depends(get_db)):
    """
    Adiciona quartos a um hotel existente.
    """
    service = HotelService(db)
    return service.add_rooms(hotel_id, rooms_in)

@router.post("/{hotel_id}/media", response_model=HotelDetail)
def add_media(hotel_id: int, media_in: List[MediaIn], db: Session = Depends(get_db)):
    """
    Adiciona mídias (fotos/vídeos) a um hotel existente.
    """
    service = HotelService(db)
    return service.add_media(hotel_id, media_in)

@router.post("/{hotel_id}/amenities", response_model=HotelDetail)
def add_amenities(hotel_id: int, amenity_ids: List[int], db: Session = Depends(get_db)):
    """
    Associa amenities existentes a um hotel.
    """
    service = HotelService(db)
    return service.add_amenities(hotel_id, amenity_ids)

