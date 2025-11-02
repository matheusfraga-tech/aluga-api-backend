# app/schemas/review.py (VERSÃO ATUALIZADA)

from pydantic import BaseModel, Field
from typing import Optional

# NOVO: Um modelo para os dados do usuário que queremos mostrar na avaliação
class ReviewUserOut(BaseModel):
    user_name: str

class ReviewBase(BaseModel):
    rating: float = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class ReviewIn(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    rating: Optional[float] = Field(None, ge=1, le=5)
    comment: Optional[str] = None

# MODIFICADO: Trocamos o 'user_id' por um objeto 'user'
class ReviewOut(ReviewBase):
    id: int
    hotel_id: int
    user: ReviewUserOut # <-- A MUDANÇA ESTÁ AQUI

    class Config:
        from_attributes = True