from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime
from app.database.database import get_db
from app.database.models import Reserva, Quarto, User
from app.helpers.auth_utils import get_current_user
from app.schemas.reserva import ReservationCreate


router = APIRouter(prefix="/reservas", tags=["reservas"])

# ------------------- CREATE -------------------
""""
@router.post("/", response_model=dict)
def create_reservation(payload: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    room = db.query(Quarto).filter(Quarto.id == payload["room_id"]).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    reservation = Reserva(
        id=str(uuid4()),
        user_id=current_user.id,
        quarto_id=room.id,
        data_checkin=datetime.fromisoformat(payload["date_checkin"]),
        data_checkout=datetime.fromisoformat(payload["date_checkout"])
    )

    db.add(reservation)
    db.commit()
    db.refresh(reservation)

    return {
        "id": reservation.id,
        "user_id": reservation.user_id,
        "room_id": reservation.quarto_id,
        "date_checkin": reservation.data_checkin.isoformat(),
        "date_checkout": reservation.data_checkout.isoformat(),
        "user": {
            "id": current_user.id,
            "user_name": current_user.user_name,
            "role": current_user.role,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name
        }
    }
"""
@router.post("/", response_model=dict)
def create_reservation(payload: ReservationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    # Cria reserva direto usando o quarto_id do JSON
    new_reservation = Reserva(
        user_id=current_user.id,
        quarto_id=payload.room_id,  #schema usa room_id
        data_checkin=payload.date_checkin,
        data_checkout=payload.date_checkout
    )

    db.add(new_reservation)
    db.commit()
    db.refresh(new_reservation)
    return {
        "id": new_reservation.id,
        "user_id": new_reservation.user_id,
        "room_id": new_reservation.quarto_id,
        "date_checkin": new_reservation.data_checkin.isoformat(),
        "date_checkout": new_reservation.data_checkout.isoformat()
    }

# ------------------- READ ALL -------------------
@router.get("/", response_model=list)
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
                "id": r.user.id if r.user else None,
                "user_name": r.user.user_name if r.user else None,
                "role": r.user.role if r.user else None,
                "first_name": r.user.first_name if r.user else None,
                "last_name": r.user.last_name if r.user else None
            }
        })
    return result

# ------------------- READ SINGLE -------------------
@router.get("/{reservation_id}", response_model=dict)
def get_reservation(reservation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    reservation = db.query(Reserva).filter(Reserva.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    return {
        "id": reservation.id,
        "user_id": reservation.user_id,
        "room_id": reservation.quarto_id,
        "date_checkin": reservation.data_checkin.isoformat(),
        "date_checkout": reservation.data_checkout.isoformat(),
        "user": {
            "id": reservation.user.id,
            "user_name": reservation.user.user_name,
            "role": reservation.user.role,
            "first_name": reservation.user.first_name,
            "last_name": reservation.user.last_name
        }
    }

# ------------------- UPDATE -------------------
@router.put("/{reservation_id}", response_model=dict)
def update_reservation(reservation_id: str, payload: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    reservation = db.query(Reserva).filter(Reserva.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    # Only owner or admin can update
    if reservation.user_id != current_user.id and current_user.role != "sysAdmin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    if "date_checkin" in payload:
        reservation.data_checkin = datetime.fromisoformat(payload["date_checkin"])
    if "date_checkout" in payload:
        reservation.data_checkout = datetime.fromisoformat(payload["date_checkout"])
    if "room_id" in payload:
        room = db.query(Quarto).filter(Quarto.id == payload["room_id"]).first()
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        reservation.quarto_id = room.id

    db.commit()
    db.refresh(reservation)

    return {
        "id": reservation.id,
        "user_id": reservation.user_id,
        "room_id": reservation.quarto_id,
        "date_checkin": reservation.data_checkin.isoformat(),
        "date_checkout": reservation.data_checkout.isoformat(),
        "user": {
            "id": reservation.user.id,
            "user_name": reservation.user.user_name,
            "role": reservation.user.role,
            "first_name": reservation.user.first_name,
            "last_name": reservation.user.last_name
        }
    }

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
