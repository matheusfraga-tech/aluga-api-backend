from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.hotel_service import HotelService
from app.schemas.hotel import HotelIn, HotelDetail, HotelCard
from app.schemas.room import RoomIn
from app.schemas.media import MediaIn
from app.schemas.hotel_filter import HotelFilter

router = APIRouter(prefix="/hotels", tags=["hotels"])

# -------------------- GET ALL HOTELS --------------------
@router.get("/", response_model=List[HotelCard])
def get_all_hotels(db: Session = Depends(get_db)):
    """
    Retorna todos os hotéis cadastrados.
    """
    service = HotelService(db)
    
    return service.get_all_hotels()

# -------------------- SEARCH --------------------
@router.get("/search")
def search_hotels(filters: HotelFilter = Depends(), db: Session = Depends(get_db)):
    service = HotelService(db)
    return service.search(filters, user_lat=filters.user_lat, user_lng=filters.user_lng)


# -------------------- CREATE FULL HOTEL --------------------
@router.post("/full", response_model=HotelDetail)
def create_full_hotel(hotel_in: HotelIn, db: Session = Depends(get_db)):
    """
    Cria o hotel junto com rooms, media e amenities em um único payload.
    """
    service = HotelService(db)
    return service.create_full(hotel_in)


# -------------------- CREATE HOTEL --------------------
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_hotel(hotel_in: HotelIn, db: Session = Depends(get_db)):
    """
    Cria um novo hotel, validando duplicidade e proximidade geográfica (~11m).
    """
    service = HotelService(db)
    try:
        hotel = service.create_hotel(hotel_in)
        return {"id": hotel.id}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# -------------------- GET HOTEL --------------------
@router.get("/{hotel_id}", response_model=HotelDetail)
def get_hotel(
    hotel_id: int,
    filters: HotelFilter = Depends(),
    db: Session = Depends(get_db)
):
    service = HotelService(db)
    hotel = service.get_hotel(
        hotel_id,
        user_lat=filters.user_lat,
        user_lng=filters.user_lng,
        check_in=filters.check_in,
        check_out=filters.check_out
    )
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return hotel


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


# -------------------- ORCHESTRATED ENDPOINTS --------------------
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
