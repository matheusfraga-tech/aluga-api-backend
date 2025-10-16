from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.amenity_repository import AmenityRepository

class AmenityService:
    def __init__(self, db: Session):
        self.repo = AmenityRepository(db)

    def get(self, amenity_id: int):
        amenity = self.repo.get(amenity_id)
        if not amenity:
            raise HTTPException(status_code=404, detail="Amenity not found")
        return amenity

    def list(self, skip: int = 0, limit: int = 100):
        return self.repo.list(skip, limit)

    def create(self, code: str, label: str):
        return self.repo.create(code, label)

    def update(self, amenity_id: int, code: str | None = None, label: str | None = None):
        amenity = self.get(amenity_id)
        return self.repo.update(amenity, code, label)

    def delete(self, amenity_id: int):
        amenity = self.get(amenity_id)
        return self.repo.delete(amenity)

