from sqlalchemy.orm import Session
from app.models.review import Review
from app.schemas.review import ReviewUpdate
from typing import List, Optional

class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, review_id: int) -> Optional[Review]:
        return self.db.query(Review).filter(Review.id == review_id).first()

    def get_by_hotel(self, hotel_id: int) -> List[Review]:
        return self.db.query(Review).filter(Review.hotel_id == hotel_id).all()

    def create(self, review: Review) -> Review:
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def update(self, db_review: Review, review_in: ReviewUpdate) -> Review:
        update_data = review_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_review, key, value)
        self.db.commit()
        self.db.refresh(db_review)
        return db_review

    def delete(self, db_review: Review) -> None:
        self.db.delete(db_review)
        self.db.commit()

    def get_all(self) -> List[Review]:
        return self.db.query(Review).all()