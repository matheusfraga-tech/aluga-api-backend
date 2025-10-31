from pydantic import BaseModel, Field
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from pydantic import field_validator
import uuid
import re


class User(BaseModel):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        title="User ID",
        description="Automatically generated unique identifier for the user."
    )

    userName: str = Field(
        min_length=3,
        max_length=15,
        title="Username",
        description="Unique username with 3 to 15 characters."
    )

    password: str = Field(
        ...,
        title="Password",
        description="Password must be at least 8 characters long, contain at least one letter, one number, and one special character.",
        pattern=re.compile(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"),
        json_schema_extra={"format": "password"}
    )

    role: str = Field(
        default="customer",
        title="Role",
        description="The role assigned to the user (e.g., admin, guest, staff)."
    )

    birthDate: datetime = Field(
        ...,
        title="Birthdate",
        description="User's birthdate. Must be at least 18 years old."
    )

    emailAddress: str = Field(
        ...,
        title="Email Address",
        description="Valid email address format (e.g., user@example.com).",
        pattern=re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    )

    phoneNumber: str = Field(
        ...,
        title="Phone Number",
        description="Valid phone number format (e.g., +55 11 98888-8888, 11988888888, +1-123-456-7890).",
        pattern=re.compile(r"^\s*(?:\+?\d{1,4}\s?)?(?:\(?\d{1,4}\)?\s?)?[\d\s\-\.\(\)]{8,15}\s*$")
    )

    firstName: str = Field(
        default="",
        title="First Name",
        description="User's first name. Can be left blank."
    )

    lastName: str = Field(
        default="",
        title="Last Name",
        description="User's last name. Can be left blank."
    )

    address: str = Field(
        default="",
        title="Address",
        description="User's address. Can be left blank."
    )

    @field_validator('birthDate')
    @classmethod
    def validate_birthdate(cls, value: datetime) -> datetime:
        age = relativedelta(date.today(), value.date()).years
        if age < 18:
            raise ValueError('You need to be at least 18 years old to book a hotel room.')
        if value.date() > date.today():
            raise ValueError(f'{value} is greater than today.')
        return value

    class Config:
        from_attributes = True
        orm_mode = True

from pydantic import BaseModel, Field
from datetime import datetime
import re

class UserSignup(BaseModel):
    userName: str = Field(
        min_length=3,
        max_length=15,
        title="Username",
        description="3–15 characters.",
        json_schema_extra={"format": "string"}
    )

    password: str = Field(
        ...,
        title="Password",
        description="Min 8 chars, must include a letter, number & symbol.",
        pattern=re.compile(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"),
        json_schema_extra={"format": "password"}
    )

    birthDate: datetime = Field(
        ...,
        title="Birthdate",
        description="Must be 18 or older.",
        json_schema_extra={"format": "date"}
    )

    emailAddress: str = Field(
        ...,
        title="Email",
        description="Enter a valid email address.",
        pattern=re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"),
        json_schema_extra={"format": "email"}
    )

    phoneNumber: str = Field(
        ...,
        title="Phone Number",
        description="Include country code if needed.",
        pattern=re.compile(r"^\s*(?:\+?\d{1,4}\s?)?(?:\(?\d{1,4}\)?\s?)?[\d\s\-\.\(\)]{8,15}\s*$"),
        json_schema_extra={"format": "string"}
    )

    firstName: str = Field(
        default="",
        title="First Name",
        description="Your first name.",
        json_schema_extra={"format": "string"}
    )

    lastName: str = Field(
        default="",
        title="Last Name",
        description="Your last name.",
        json_schema_extra={"format": "string"}
    )

    address: str = Field(
        default="",
        title="Address",
        description="Your address.",
        json_schema_extra={"format": "string"}
    )


    @field_validator('birthDate')
    @classmethod
    def validate_birthdate(cls, value: datetime) -> datetime:
        age = relativedelta(date.today(), value.date()).years
        if age < 18:
            raise ValueError('You need to be at least 18 years old to book a hotel room.')
        if value.date() > date.today():
            raise ValueError(f'{value} is greater than today.')
        return value

    class Config:
        from_attributes = True
        orm_mode = True

class UserOut(BaseModel):

    id:  str = Field(default_factory=lambda: str(uuid.uuid4()))
    userName: str = Field(min_length=3, max_length=15) # validade unique
    role: str
    birthDate: datetime
    emailAddress: str = Field(
        pattern=re.compile(
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        )
    )  # ex: test@test.com
    phoneNumber: str = Field(
        pattern=re.compile(
            r"^\s*(?:\+?\d{1,4}\s?)?(?:\(?\d{1,4}\)?\s?)?[\d\s\-\.\(\)]{8,15}\s*$"
        )
    )  # ex: 11988888888, +55 11 98888-8888
    firstName: str | None = None
    lastName: str | None = None
    address: str | None = None

    class Config:
        from_attributes = True
        orm_mode = True