from sqlalchemy.orm import Session
from app.models.amenity import Amenity

class AmenityRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, amenity_id: int) -> Amenity | None:
        return self.db.query(Amenity).filter(Amenity.id == amenity_id).first()

    def list(self, skip: int = 0, limit: int = 100) -> list[Amenity]:
        return self.db.query(Amenity).offset(skip).limit(limit).all()

    def create(self, code: str, label: str) -> Amenity:
        amenity = Amenity(code=code, label=label)
        self.db.add(amenity)
        self.db.commit()
        self.db.refresh(amenity)
        return amenity

    def update(self, amenity: Amenity, code: str | None = None, label: str | None = None) -> Amenity:
        if code:
            amenity.code = code
        if label:
            amenity.label = label
        self.db.commit()
        self.db.refresh(amenity)
        return amenity

    def delete(self, amenity: Amenity) -> Amenity:
        self.db.delete(amenity)
        self.db.commit()
        return amenity

