from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
from sqlalchemy import func

from app.repositories.review_repository import ReviewRepository
from app.repositories.hotel_repository import HotelRepository
from app.repositories.user_repository import UserRepository
from app.models.review import Review
from app.models.hotel import Hotel
from app.schemas.review import ReviewIn, ReviewUpdate, ReviewOut, ReviewUserOut
from app.schemas.user import User


class ReviewService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ReviewRepository(db)
        self.hotel_repo = HotelRepository()
        self.user_repo = UserRepository(db)

    def _calculate_and_update_hotel_stars(self, hotel_id: int):
        avg_rating_result = self.db.query(func.avg(Review.rating)).filter(
            Review.hotel_id == hotel_id
        ).scalar()
        
        calculated_stars = 0.0
        if avg_rating_result is not None and avg_rating_result > 0:
            calculated_stars = round(avg_rating_result, 1)
            
        hotel_to_update = self.db.query(Hotel).filter(Hotel.id == hotel_id).first()
        
        if hotel_to_update:
            hotel_to_update.stars = calculated_stars
            self.db.commit()

    def _enrich_review(self, review: Review) -> ReviewOut:
        user = self.user_repo.get_by_id(review.user_id)
        user_name = user.userName if user else "Usuário Desconhecido"
        
        user_data_for_review = ReviewUserOut(
            user_name=user_name
        )
        return ReviewOut(
            id=review.id, hotel_id=review.hotel_id,
            rating=review.rating, comment=review.comment,
            user=user_data_for_review
        )

    def get_reviews_for_hotel(self, hotel_id: int) -> List[ReviewOut]:
        if not self.hotel_repo.get(db=self.db, hotel_id=hotel_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")
        
        raw_reviews = self.repo.get_by_hotel(hotel_id)
        return [self._enrich_review(review) for review in raw_reviews]

    def create_review(self, hotel_id: int, current_user: User, review_in: ReviewIn) -> ReviewOut:
        if not self.hotel_repo.get(db=self.db, hotel_id=hotel_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")

        db_review = Review(
            hotel_id=hotel_id, user_id=current_user.id,
            rating=review_in.rating, comment=review_in.comment
        )
        created_review = self.repo.create(db_review)
        
        self._calculate_and_update_hotel_stars(hotel_id)
        
        return self._enrich_review(created_review)

    def update_review(self, review_id: int, current_user: User, review_update: ReviewUpdate) -> ReviewOut:
        db_review = self.repo.get(review_id)
        if not db_review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
        
        if db_review.user_id != current_user.id and current_user.role != "sysAdmin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
            
        updated_review = self.repo.update(db_review, review_update)
        
        self._calculate_and_update_hotel_stars(updated_review.hotel_id)
        
        return self._enrich_review(updated_review)

    def delete_review(self, review_id: int, current_user: User):
        db_review = self.repo.get(review_id)
        if not db_review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
        
        if db_review.user_id != current_user.id and current_user.role != "sysAdmin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
            
        hotel_id = db_review.hotel_id
        self.repo.delete(db_review)
        
        self._calculate_and_update_hotel_stars(hotel_id)

    def get_all_reviews(self) -> List[ReviewOut]:
        raw_reviews = self.repo.get_all()
        return [self._enrich_review(review) for review in raw_reviews]