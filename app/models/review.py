from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
# --- MUDANÇA AQUI ---
from sqlalchemy import Float, Text, ForeignKey, String
from app.models.base import Base, IntPKMixin

class Review(IntPKMixin, Base):
    __tablename__ = "reviews"

    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id", ondelete="CASCADE"), index=True)
    # --- MUDANÇA AQUI ---
    user_id: Mapped[str] = mapped_column(String, index=True)
    rating: Mapped[float] = mapped_column(Float)
    comment: Mapped[str | None] = mapped_column(Text(), nullable=True)

    hotel: Mapped["Hotel"] = relationship("Hotel", back_populates="reviews")