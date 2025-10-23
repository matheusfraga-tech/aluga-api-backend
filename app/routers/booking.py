from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime
from typing import List
from sqlalchemy.orm import joinedload

from app.database.database import get_db
from app.models.booking import Booking as Reserva 
from app.models.room import Room as Quarto 
from app.models.user import User 
from app.services.auth_service import get_current_user
from app.schemas.booking import ReservationCreate, ReservationOut, ReservationUpdate


# Ajustando o prefixo da rota para 'bookings'
router = APIRouter(prefix="/bookings", tags=["reservations"])

# ------------------- CREATE -------------------
@router.post("/", response_model=dict)
def create_reservation(payload: ReservationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    # Cria reserva direto usando o quarto_id do JSON
    new_reservation = Reserva(
        # CORRIGIDO: O atributo no modelo ORM deve ser 'userId'
        userId=current_user.id,
        quarto_id=payload.room_id, #schema usa room_id
        data_checkin=payload.date_checkin,
        data_checkout=payload.date_checkout
    )

    db.add(new_reservation)
    db.commit()
    db.refresh(new_reservation)
    return {
        "id": new_reservation.id,
        # CORRIGIDO: Lendo o atributo 'userId' do ORM
        "user_id": new_reservation.userId,
        "room_id": new_reservation.quarto_id,
        "date_checkin": new_reservation.data_checkin.isoformat(),
        "date_checkout": new_reservation.data_checkout.isoformat()
    }

# ------------------- READ ALL (usuário logado apenas) -------------------
@router.get("/", response_model=List[ReservationOut])
def get_reservas(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Buscar apenas as reservas do usuário logado
    # CORRIGIDO: Usando 'Reserva' como alias e 'userId' como atributo
    reservas = db.query(Reserva).filter(Reserva.userId == current_user.id).all()
    return reservas

# ------------------- READ SINGLE -------------------
@router.get("/{reserva_id}", response_model=ReservationOut)
def get_reserva(reserva_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Buscar reserva pelo id e pelo usuário logado
    reserva = db.query(Reserva).filter(
        Reserva.id == reserva_id,
        # CORRIGIDO: Usando 'userId' como atributo
        Reserva.userId == current_user.id 
    ).first()

    if not reserva:
        raise HTTPException(status_code=404, detail="Reservation not found")

    return reserva

# ------------------- UPDATE -------------------
@router.patch("/{reserva_id}", response_model=ReservationOut)
def update_reserva(
    reserva_id: str,
    reserva_update: ReservationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    reserva = db.query(Reserva).filter(
        Reserva.id == reserva_id,
        # CORRIGIDO: Usando 'userId' como atributo
        Reserva.userId == current_user.id 
    ).first()

    if not reserva:
        raise HTTPException(status_code=404, detail="Reservation not found")

    # Atualiza apenas os campos fornecidos
    if reserva_update.date_checkin is not None:
        reserva.data_checkin = reserva_update.date_checkin
    if reserva_update.date_checkout is not None:
        reserva.data_checkout = reserva_update.date_checkout
    if reserva_update.room_id is not None:
        reserva.quarto_id = reserva_update.room_id

    db.commit()
    db.refresh(reserva)

    return reserva

# ------------------- DELETE -------------------
@router.delete("/{reservation_id}", response_model=dict)
def delete_reservation(reservation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    reservation = db.query(Reserva).filter(Reserva.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    # CORRIGIDO: Usando 'userId' como atributo no check de permissão
    if reservation.userId != current_user.id and current_user.role != "sysAdmin": 
        raise HTTPException(status_code=403, detail="Access denied")

    db.delete(reservation)
    db.commit()
    return {"message": f"Reservation {reservation_id} deleted successfully"}
