from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from app.models.base import Base, IntPKMixin, hotel_amenities, room_amenities

class Amenity(IntPKMixin, Base):
    __tablename__ = "amenities"

    code: Mapped[str] = mapped_column(String(60), unique=True, index=True, nullable=False)
    label: Mapped[str] = mapped_column(String(120), nullable=False)

    hotels: Mapped[list["Hotel"]] = relationship(
        "Hotel",
        secondary=hotel_amenities,
        back_populates="amenities",
        lazy="selectin"
    )
    rooms: Mapped[list["Room"]] = relationship(
        "Room",
        secondary=room_amenities,
        back_populates="amenities",
        lazy="selectin"
    )

