# app/routers/review_router.py (VERSÃO FINAL COM LOGIN FALSO INTEGRADO)

from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from enum import Enum

from app.database import get_db
from app.services.review_service import ReviewService
from app.schemas.review import ReviewIn, ReviewUpdate, ReviewOut
from app.schemas.user import User
from app.helpers.auth_utils import fake_users_db

router = APIRouter(prefix="/reviews", tags=["Reviews"])

# --- LÓGICA DO LOGIN DE TESTE (Tudo dentro deste arquivo) ---

# 1. Variável para guardar o usuário "logado"
_current_test_user: Optional[User] = None

# 2. Lista de usuários para o dropdown do nosso endpoint de login falso
class TestUser(str, Enum):
    john_doe = "john_doe"
    maria_lee = "maria_lee"
    james_wong = "james_wong"
    emily_nguyen = "emily_nguyen"
    oliver_smith = "oliver_smith"

# 3. Endpoint para "fazer o login" de teste
@router.post("/login-as-test-user", summary="Simula um login para testes (isolado para reviews)")
def mock_review_login(user_to_simulate: TestUser = Query(..., description="Escolha com qual usuário você quer agir.")):
    """
    Define qual usuário será considerado 'logado' para os endpoints de avaliação.
    Esta escolha fica salva na memória do servidor até que ele seja reiniciado.
    """
    global _current_test_user
    user_found = None
    for user_dict in fake_users_db.values():
        if user_dict["userName"] == user_to_simulate.value:
            user_found = User(**user_dict)
            break
    
    if not user_found:
        raise HTTPException(404, "Usuário de teste não encontrado.")

    _current_test_user = user_found
    return {"message": f"Sucesso! Para os endpoints de avaliação, você agora está agindo como: '{user_found.userName}'"}

# 4. Dependência que os endpoints usarão para pegar o usuário "logado"
def get_current_test_user() -> User:
    if _current_test_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nenhum usuário de teste 'logado'. Por favor, use o endpoint /reviews/login-as-test-user primeiro."
        )
    return _current_test_user

# --- ENDPOINTS ORIGINAIS DO CRUD DE AVALIAÇÃO ---

@router.get("/hotels/{hotel_id}/reviews", response_model=List[ReviewOut])
def get_reviews_for_hotel(hotel_id: int, db: Session = Depends(get_db)):
    """Obtém todas as avaliações para um hotel específico."""
    service = ReviewService(db)
    return service.get_reviews_for_hotel(hotel_id)

@router.post("/hotels/{hotel_id}/reviews", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
def create_review(
    hotel_id: int,
    review_in: ReviewIn,
    db: Session = Depends(get_db),
    # MODIFICADO: Usamos a dependência que pega o usuário "logado" do teste
    current_user: User = Depends(get_current_test_user)
):
    """Cria uma nova avaliação para um hotel."""
    service = ReviewService(db)
    return service.create_review(hotel_id=hotel_id, current_user=current_user, review_in=review_in)

@router.put("/{review_id}", response_model=ReviewOut)
def update_review(
    review_id: int,
    review_update: ReviewUpdate,
    db: Session = Depends(get_db),
    # MODIFICADO: Usamos a dependência que pega o usuário "logado" do teste
    current_user: User = Depends(get_current_test_user)
):
    """Atualiza uma avaliação existente."""
    service = ReviewService(db)
    return service.update_review(review_id=review_id, current_user=current_user, review_update=review_update)

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    # MODIFICADO: Usamos a dependência que pega o usuário "logado" do teste
    current_user: User = Depends(get_current_test_user)
):
    """Deleta uma avaliação."""
    service = ReviewService(db)
    service.delete_review(review_id=review_id, current_user=current_user)
    return None 