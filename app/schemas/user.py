from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import uuid
import re

class User(BaseModel):
    id:  str = Field(default_factory=lambda: str(uuid.uuid4()))
    userName: str = Field(min_length=3, max_length=15) # validade unique
    password: str = Field(pattern=re.compile(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$")) 
        #8 chars, at least 1 uppercase, at least 1 number, 1 special char
    role: str
    birthDate: datetime
    emailAddress: str = Field(
        pattern=re.compile(
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        )
    )  # ex: test@test.com
    phoneNumber: str = Field(
        pattern=re.compile(
            r"^\s*(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(: *x(\d+))?\s*$"
        )
    )  # ex: 11988888888
    firstName: str | None = None
    lastName: str | None = None
    address: str | None = None

    @field_validator('birthDate')
    @classmethod
    def validate_birthdate(cls, value: datetime) -> datetime:
        age = relativedelta(date.today(), value.date()).years
        if age < 18:
            raise ValueError('You need to be at least 18 years old to book a hotel room')
        if value.date() > date.today():
            raise ValueError(f'{value} is greater than today')
        return value

    class Config:
        from_attributes = True

