from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Float, Integer, Text, ForeignKey
from app.models.base import Base, IntPKMixin

class Review(IntPKMixin, Base):
    __tablename__ = "reviews"

    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text(), nullable=True)

    hotel: Mapped["Hotel"] = relationship("Hotel", back_populates="reviews")

