from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from .user import User
import uuid

class Reserva(Base):
    __tablename__ = "reservas"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    data_checkin = Column(DateTime, nullable=False)
    data_checkout = Column(DateTime, nullable=False)

    user = relationship("User")
    room = relationship("Room")