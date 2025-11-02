from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import Table, Column, Integer, ForeignKey

Base = declarative_base()

# Mixin para ID auto-increment
class IntPKMixin:
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

# Tabelas de associação (many-to-many)
hotel_amenities = Table(
    "hotel_amenities",
    Base.metadata,
    Column("hotel_id", Integer, ForeignKey("hotels.id", ondelete="CASCADE"), primary_key=True),
    Column("amenity_id", Integer, ForeignKey("amenities.id", ondelete="CASCADE"), primary_key=True),
)

room_amenities = Table(
    "room_amenities",
    Base.metadata,
    Column("room_id", Integer, ForeignKey("rooms.id", ondelete="CASCADE"), primary_key=True),
    Column("amenity_id", Integer, ForeignKey("amenities.id", ondelete="CASCADE"), primary_key=True),
)

