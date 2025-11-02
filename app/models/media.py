from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from app.models.base import Base, IntPKMixin

class Media(IntPKMixin, Base):
    __tablename__ = "media"

    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id", ondelete="CASCADE"), index=True, nullable=False)
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    kind: Mapped[str] = mapped_column(String(30), default="photo", nullable=False)  # photo | video

    hotel: Mapped["Hotel"] = relationship("Hotel", back_populates="media")

