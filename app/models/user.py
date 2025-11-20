from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime
from datetime import datetime
from .base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .booking import Booking

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, nullable=False, index=True)
    userName: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    birthDate: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    emailAddress: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    phoneNumber: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    firstName: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    lastName: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    address: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    
    # Relacionamento com bookings
    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="user")
