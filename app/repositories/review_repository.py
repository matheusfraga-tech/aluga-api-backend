# app/repositories/review_repository.py

from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.review import ReviewUpdate

# --- BANCO DE DADOS EM MEMÓRIA PARA AVALIAÇÕES ---
fake_reviews_db = []
review_id_counter = 0

class ReviewRepository:
    def __init__(self, db: Session):
        # A sessão do banco de dados (db) é ignorada nesta versão em memória
        pass

    def get(self, review_id: int) -> Optional[dict]:
        """Busca uma avaliação na lista em memória pelo ID."""
        print(f"--- ReviewRepository: Buscando review com id={review_id} ---")
        return next((review for review in fake_reviews_db if review["id"] == review_id), None)

    def get_by_hotel(self, hotel_id: int) -> List[dict]:
        """Busca todas as avaliações de um hotel na lista em memória."""
        print(f"--- ReviewRepository: Buscando reviews para o hotel_id={hotel_id} ---")
        return [review for review in fake_reviews_db if review["hotel_id"] == hotel_id]

    def create(self, review_model) -> dict:
        """Cria uma nova avaliação na lista em memória."""
        global review_id_counter
        review_id_counter += 1
        
        new_review = {
            "id": review_id_counter,
            "hotel_id": review_model.hotel_id,
            "user_id": review_model.user_id,
            "rating": review_model.rating,
            "comment": review_model.comment,
        }
        fake_reviews_db.append(new_review)
        print(f"--- ReviewRepository: Review criado: {new_review} ---")
        print(f"--- Estado atual do BD em memória: {fake_reviews_db} ---")
        return new_review

    def update(self, db_review: dict, review_in: ReviewUpdate) -> dict:
        """Atualiza uma avaliação na lista em memória."""
        update_data = review_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            db_review[key] = value
        print(f"--- ReviewRepository: Review atualizado: {db_review} ---")
        return db_review

    def delete(self, db_review: dict) -> None:
        """Deleta uma avaliação da lista em memória."""
        print(f"--- ReviewRepository: Deletando review: {db_review} ---")
        fake_reviews_db.remove(db_review)
        print(f"--- Estado atual do BD em memória: {fake_reviews_db} ---")