
from __future__ import annotations

from .base import (
    Base,
    IntPKMixin,
    hotel_amenities,
    room_amenities
)

from .hotel import Hotel
from .room import Room
from .amenity import Amenity
from .booking import Booking
from .media import Media
from .review import Review
from .user import User
from .booking import Booking

all_models = [
    Hotel,
    Room,
    Amenity,
    Booking,
    Media,
    Review,
    User,
    Booking
]

