from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime
from app.database.database import get_db
from app.models.reserva import Reserva
from app.models.room import Room
from app.models.base import Base
from app.schemas.user import User
from app.helpers.auth_utils import get_current_user
from app.schemas.reserva import ReservationCreate, ReservationOut, ReservationUpdate
from typing import List
from sqlalchemy.orm import joinedload


router = APIRouter(prefix="/reservas", tags=["reservas"])

# ------------------- CREATE -------------------
@router.post("/reservas/")
def create_reservation(
    reserva_data: ReservationCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    nova_reserva = Reserva(
        user_id=current_user.id, 
        quarto_id=reserva_data.quarto_id,
        data_checkin=reserva_data.data_checkin,
        data_checkout=reserva_data.data_checkout
    )
    db.add(nova_reserva)
    db.commit()
    db.refresh(nova_reserva)
    return nova_reserva
# ------------------- READ ALL -------------------
"""@router.get("/", response_model=list)
def list_reservations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    reservations = db.query(Reserva).all()
    result = []
    for r in reservations:
        result.append({
            "id": r.id,
            "user_id": r.user_id,
            "room_id": r.quarto_id,
            "date_checkin": r.data_checkin.isoformat(),
            "date_checkout": r.data_checkout.isoformat(),
            "user": {
                "id": r.user_id if r.user else None,
                "user_name": r.user.user_name if r.user else None,
                "role": r.user.role if r.user else None,
                "first_name": r.user.first_name if r.user else None,
                "last_name": r.user.last_name if r.user else None
            }
        })
    return result"""
# ------------------- READ ALL (usuário logado apenas) -------------------
@router.get("/", response_model=List[ReservationOut])
def get_reservas(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Buscar apenas as reservas do usuário logado
    reservas = db.query(Reserva).filter(Reserva.user_id == current_user.id).all()
    return reservas

# ------------------- READ SINGLE -------------------
@router.get("/{reserva_id}", response_model=ReservationOut)
def get_reserva(reserva_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Buscar reserva pelo id e pelo usuário logado
    reserva = db.query(Reserva).filter(
        Reserva.id == reserva_id,
        Reserva.user_id == current_user.id
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
        Reserva.user_id == current_user.id
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
    if reservation.user_id != current_user.id and current_user.role != "sysAdmin":
        raise HTTPException(status_code=403, detail="Access denied")

    db.delete(reservation)
    db.commit()
    return {"message": f"Reservation {reservation_id} deleted successfully"}
