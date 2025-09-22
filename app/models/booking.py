from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Date, Integer
from datetime import date
from app.models.base import Base, IntPKMixin

class Booking(IntPKMixin, Base):
    __tablename__ = "bookings"

    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id", ondelete="CASCADE"), index=True, nullable=False)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"), index=True, nullable=False)
    check_in: Mapped[date] = mapped_column(Date, nullable=False)
    check_out: Mapped[date] = mapped_column(Date, nullable=False)
    rooms_booked: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    hotel: Mapped["Hotel"] = relationship("Hotel", back_populates="bookings")
    room: Mapped["Room"] = relationship("Room", back_populates="bookings")

