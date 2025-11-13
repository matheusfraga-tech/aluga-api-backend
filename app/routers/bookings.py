from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.booking import Booking
from app.models.room import Room
from app.models.hotel import Hotel
from app.schemas.user import User
from app.services.auth_service import get_current_user
from app.schemas.booking import BookingCreate, BookingOut, BookingUpdate, BookingWithDetails
from typing import List
from sqlalchemy.orm import joinedload
from app.services.hotel_metrics_service import HotelMetricsService 


router = APIRouter(prefix="/bookings", tags=["bookings"])

# ------------------- CREATE -------------------
@router.post("/", response_model=BookingWithDetails)
def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    metrics_service = HotelMetricsService(db) 
    
    # Verifica quarto
    room = db.query(Room).filter(Room.id == booking_data.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail=f"Quarto {booking_data.room_id} não encontrado")

    # Verifica hotel
    hotel = db.query(Hotel).filter(Hotel.id == booking_data.hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=404, detail=f"Hotel {booking_data.hotel_id} não encontrado")
    
    hotel_id = booking_data.hotel_id 

    new_booking = Booking(
        user_id=current_user.id,
        hotel_id=hotel_id,
        room_id=booking_data.room_id,
        check_in=booking_data.check_in,
        check_out=booking_data.check_out,
        rooms_booked=booking_data.rooms_booked or 1,
    )

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    # Dispara o recálculo da popularidade
    metrics_service.calculate_and_update_metrics(hotel_id)

    # Retorna com hotel e quarto carregados
    return db.query(Booking)\
        .options(
            joinedload(Booking.hotel),
            joinedload(Booking.room)
        )\
        .filter(Booking.id == new_booking.id)\
        .first()

# ------------------- READ ALL (SÓ DO USUÁRIO LOGADO) -------------------
@router.get("/", response_model=List[BookingWithDetails])
def get_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bookings = (
        db.query(Booking)
        .filter(Booking.user_id == current_user.id)
        .options(
            joinedload(Booking.hotel),
            joinedload(Booking.room)
        )
        .all()
    )
    return bookings

# ------------------- READ SINGLE -------------------
@router.get("/{booking_id}", response_model=BookingWithDetails)
def get_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    booking = (
        db.query(Booking)
        .options(
            joinedload(Booking.hotel),
            joinedload(Booking.room)
        )
        .filter(Booking.id == booking_id, Booking.user_id == current_user.id)
        .first()
    )

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    return booking

# ------------------- UPDATE -------------------
@router.patch("/{booking_id}", response_model=BookingWithDetails)
def update_booking(
    booking_id: int,
    booking_update: BookingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = (
        db.query(Booking)
        .filter(Booking.id == booking_id, Booking.user_id == current_user.id)
        .first()
    )
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Atualiza datas
    if booking_update.check_in is not None:
        booking.check_in = booking_update.check_in
    if booking_update.check_out is not None:
        booking.check_out = booking_update.check_out

    # Atualiza room_id somente se o quarto existe
    if booking_update.room_id is not None:
        room = db.query(Room).filter(Room.id == booking_update.room_id).first()
        if not room:
            raise HTTPException(status_code=404, detail=f"Room with id {booking_update.room_id} not found")
        booking.room_id = booking_update.room_id

    # Atualiza hotel_id somente se o hotel existe
    if booking_update.hotel_id is not None:
        hotel = db.query(Hotel).filter(Hotel.id == booking_update.hotel_id).first()
        if not hotel:
            raise HTTPException(status_code=404, detail=f"Hotel with id {booking_update.hotel_id} not found")
        booking.hotel_id = booking_update.hotel_id

    # Atualiza quantidade de quartos
    if booking_update.rooms_booked is not None:
        booking.rooms_booked = booking_update.rooms_booked

    db.commit()
    
    # Recarrega com relacionamentos
    db.refresh(booking)
    return db.query(Booking)\
        .options(
            joinedload(Booking.hotel),
            joinedload(Booking.room)
        )\
        .filter(Booking.id == booking_id)\
        .first()

# ------------------- DELETE -------------------
@router.delete("/{booking_id}", response_model=dict)
def delete_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    metrics_service = HotelMetricsService(db)

    booking = (
        db.query(Booking)
        .filter(Booking.id == booking_id, Booking.user_id == current_user.id)
        .first()
    )
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    hotel_id = booking.hotel_id
    
    db.delete(booking)
    db.commit()
    
    # Dispara o recálculo da popularidade
    metrics_service.calculate_and_update_metrics(hotel_id)
    
    return {"message": f"Booking {booking_id} deleted successfully"}