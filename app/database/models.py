from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base

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

class Reserva(Base):
    __tablename__ = "reservas"
    id = Column(Integer, primary_key=True, index=True)
    cliente = Column(String)
    data_checkin = Column(DateTime)
    data_checkout = Column(DateTime)
    quarto_id = Column(Integer, ForeignKey("quartos.id"))
    quarto = relationship("Quarto", back_populates="reservas")