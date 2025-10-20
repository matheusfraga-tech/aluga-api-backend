from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Float
from app.models.base import IntPKMixin, hotel_amenities
from app.database import Base, engine
from sqlalchemy import DateTime
from datetime import datetime

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

Base.metadata.create_all(bind=engine)