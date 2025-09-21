from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..database.models import Reserva
from ..schemas.reserva import ReservaCreate, ReservaOut

router = APIRouter(
    prefix="/reservas",
    tags=["reservas"]
)

@router.post("/", response_model=ReservaOut)
def criar_reserva(reserva: ReservaCreate, db: Session = Depends(get_db)):
    db_reserva = Reserva(**reserva.dict())
    db.add(db_reserva)
    db.commit()
    db.refresh(db_reserva)
    return db_reserva

@router.get("/", response_model=list[ReservaOut])
def listar_reservas(db: Session = Depends(get_db)):
    return db.query(Reserva).all()

@router.delete("/{reserva_id}")
def deletar_reserva(reserva_id: int, db: Session = Depends(get_db)):
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
    db.delete(reserva)
    db.commit()
    return {"message": f"Reserva {reserva_id} deletada com sucesso"}
