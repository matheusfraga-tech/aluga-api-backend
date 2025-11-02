from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float, ForeignKey
from app.models.base import Base, IntPKMixin, room_amenities

class Room(IntPKMixin, Base):
    __tablename__ = "rooms"

    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    room_type: Mapped[str] = mapped_column(String(60), index=True, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    base_price: Mapped[float] = mapped_column(Float, nullable=False)
    total_units: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    hotel: Mapped["Hotel"] = relationship("Hotel", back_populates="rooms")
    
    amenities: Mapped[list["Amenity"]] = relationship(
        "Amenity",
        secondary=room_amenities,
        back_populates="rooms",
        lazy="selectin"
    )
    
    bookings: Mapped[list["Booking"]] = relationship(
        "Booking",
        back_populates="room",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    


