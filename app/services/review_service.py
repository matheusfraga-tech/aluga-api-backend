# app/services/review_service.py (VERSÃO PARA TESTE ISOLADO)

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List

from app.repositories.review_repository import ReviewRepository
from app.repositories.hotel_repository import HotelRepository
from app.models.review import Review
from app.schemas.review import ReviewIn, ReviewUpdate, ReviewOut, ReviewUserOut
from app.schemas.user import User
from app.helpers.auth_utils import fake_users_db

class ReviewService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ReviewRepository(db)
        self.hotel_repo = HotelRepository()

    def _enrich_review(self, review: dict) -> ReviewOut:
        # (Esta função continua a mesma de antes)
        user_id = review.get("user_id")
        user_info = fake_users_db.get(user_id)
        user_data_for_review = ReviewUserOut(
            user_name=user_info.get("userName") if user_info else "Usuário Desconhecido"
        )
        return ReviewOut(
            id=review.get("id"), hotel_id=review.get("hotel_id"),
            rating=review.get("rating"), comment=review.get("comment"),
            user=user_data_for_review
        )

    def get_reviews_for_hotel(self, hotel_id: int) -> List[ReviewOut]:
        """Busca todas as avaliações de um hotel."""
        # --- MODIFICADO PARA TESTE: Verificação de hotel desativada ---
        # if not self.hotel_repo.get(db=self.db, hotel_id=hotel_id):
        #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")
        
        raw_reviews = self.repo.get_by_hotel(hotel_id)
        return [self._enrich_review(review) for review in raw_reviews]

    def create_review(self, hotel_id: int, current_user: User, review_in: ReviewIn) -> ReviewOut:
        """Cria uma nova avaliação para um hotel."""
        # --- MODIFICADO PARA TESTE: Verificação de hotel desativada ---
        # if not self.hotel_repo.get(db=self.db, hotel_id=hotel_id):
        #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")

        review_data = Review(
            hotel_id=hotel_id, user_id=current_user.id,
            rating=review_in.rating, comment=review_in.comment
        )
        created_review = self.repo.create(review_data)
        return self._enrich_review(created_review)

    # O resto do arquivo (update e delete) não depende do repositório de hotel, então não precisa de mudanças.
    def update_review(self, review_id: int, current_user: User, review_update: ReviewUpdate) -> ReviewOut:
        db_review = self.repo.get(review_id)
        if not db_review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
        if db_review["user_id"] != current_user.id and current_user.role != "sysAdmin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        updated_review = self.repo.update(db_review, review_update)
        return self._enrich_review(updated_review)

    def delete_review(self, review_id: int, current_user: User):
        db_review = self.repo.get(review_id)
        if not db_review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
        if db_review["user_id"] != current_user.id and current_user.role != "sysAdmin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        self.repo.delete(db_review)