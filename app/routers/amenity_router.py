
# routers/amenity_router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.amenity import AmenityOut
from app.services.amenity_service import AmenityService

router = APIRouter(prefix="/amenities", tags=["Amenities"])

@router.post("/", response_model=AmenityOut)
def create_amenity(code: str, label: str, db: Session = Depends(get_db)):
    return AmenityService(db).create(code, label)

@router.get("/", response_model=list[AmenityOut])
def list_amenities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return AmenityService(db).list(skip, limit)

@router.get("/{amenity_id}", response_model=AmenityOut)
def read_amenity(amenity_id: int, db: Session = Depends(get_db)):
    return AmenityService(db).get(amenity_id)

@router.put("/{amenity_id}", response_model=AmenityOut)
def update_amenity(amenity_id: int, code: str | None = None, label: str | None = None, db: Session = Depends(get_db)):
    return AmenityService(db).update(amenity_id, code, label)

@router.delete("/{amenity_id}", response_model=AmenityOut)
def delete_amenity(amenity_id: int, db: Session = Depends(get_db)):
    return AmenityService(db).delete(amenity_id)

