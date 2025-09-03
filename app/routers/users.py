from typing import Union
from fastapi import APIRouter, Depends, HTTPException
from pydantic  import BaseModel, Field, field_validator
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from .. import dependencies
import uuid
import re

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

class User(BaseModel):
    id:  str = Field(default_factory=lambda: str(uuid.uuid4()))
    userName: str = Field(min_length=3, max_length=15)
    password: str = Field(pattern=re.compile(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$")) 
        #8 chars, at least 1 uppercased, at least 1 number, 1 special char
    type: str
    birthDate: datetime
    @field_validator('birthDate')
    @classmethod
    def is_valid(cls, value: datetime) -> datetime:
        if((relativedelta(date.today(), value.date()).years) < 18):
            raise ValueError(f'You need to be at least 18 years old to book a hotel room')
        if value.date() > date.today():
            raise ValueError(f'{value} is greater than today')
        return value
    emailAddress: str = Field(pattern=re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"))
        #test@test.com
        #test.test@test.com
    phoneNumber: str = Field(pattern=re.compile(r"^\s*(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(: *x(\d+))?\s*$"))
        #11988888888
    firstName: str  | None
    lastName: str   | None
    address: str    | None

@router.get("/", dependencies=[Depends(dependencies.check_admin_role)])
def read_root():
    return dependencies.fake_users_db

@router.get("/{userName}", dependencies=[Depends(dependencies.check_admin_role)])
def read_root(userName: str):
    if(dependencies.fake_users_db.get(userName) == None):
        raise HTTPException(status_code=404, detail="User not found")
    return dependencies.fake_users_db.get(userName)

@router.post("/register")
async def create_item(user: User):
    #create user record
    #create primary contact record
    #relate both records
    return user