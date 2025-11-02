# app/routers/review_router.py (VERSÃO FINAL - AUTENTICAÇÃO REAL)

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.services.review_service import ReviewService
from app.schemas.review import ReviewIn, ReviewUpdate, ReviewOut
from app.schemas.user import User
from app.services import auth_service

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.get("/hotels/{hotel_id}/reviews", response_model=List[ReviewOut])
def get_reviews_for_hotel(hotel_id: int, db: Session = Depends(get_db)):
    service = ReviewService(db)
    return service.get_reviews_for_hotel(hotel_id)

@router.post("/hotels/{hotel_id}/reviews", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
def create_review(
    hotel_id: int,
    review_in: ReviewIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    service = ReviewService(db)
    return service.create_review(hotel_id=hotel_id, current_user=current_user, review_in=review_in)

@router.put("/{review_id}", response_model=ReviewOut)
def update_review(
    review_id: int,
    review_update: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    service = ReviewService(db)
    return service.update_review(review_id=review_id, current_user=current_user, review_update=review_update)

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    service = ReviewService(db)
    service.delete_review(review_id=review_id, current_user=current_user)
    return None