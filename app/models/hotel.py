from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Float
from app.models.base import Base, IntPKMixin, hotel_amenities

class Hotel(IntPKMixin, Base):
    __tablename__ = "hotels"

    name: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    city: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    neighborhood: Mapped[str | None] = mapped_column(String(120), nullable=True)
    address: Mapped[str | None] = mapped_column(String(200), nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    stars: Mapped[float] = mapped_column(Float, default=0.0, index=True)
    popularity: Mapped[float] = mapped_column(Float, default=0.0, index=True)
    policies: Mapped[str | None] = mapped_column(Text(), nullable=True)

    rooms: Mapped[list["Room"]] = relationship(
        "Room",
        back_populates="hotel",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    amenities: Mapped[list["Amenity"]] = relationship(
        "Amenity",
        secondary=hotel_amenities,
        back_populates="hotels",
        lazy="selectin"
    )

    media: Mapped[list["Media"]] = relationship(
        "Media",
        back_populates="hotel",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    bookings: Mapped[list["Booking"]] = relationship(
        "Booking",
        back_populates="hotel",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    reviews: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="hotel",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
