from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    user_name = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)
    email_address = Column(String, unique=True, nullable=False)
    phone_number = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    address = Column(String)
    
    reservas = relationship("Reserva", back_populates="user")

class Reserva(Base):
    __tablename__ = "reservas"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    quarto_id = Column(Integer, ForeignKey("quartos.id"), nullable=False)
    data_checkin = Column(DateTime, nullable=False)
    data_checkout = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="reservas")
    quarto = relationship("Quarto", back_populates="reservas")

class Hotel(Base):
    __tablename__ = "hoteis"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, index=True)
    quartos = relationship("Quarto", back_populates="hotel")

class Quarto(Base):
    __tablename__ = "quartos"
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String)
    hotel_id = Column(Integer, ForeignKey("hoteis.id"))
    hotel = relationship("Hotel", back_populates="quartos")
    reservas = relationship("Reserva", back_populates="quarto")
