from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from jwt import PyJWTError
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
#from passlib.context import CryptContext
from pydantic import BaseModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# should be in schemas/
class Token(BaseModel):
    access_token: str
    token_type: str
class DataToken(BaseModel):
    id: str

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})  # this will be properly interpreted by JWT

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token_access(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        print(user_id)
        if user_id is None:
            raise credentials_exception
        token_data = DataToken(id=user_id)
    except (PyJWTError, InvalidTokenError) as e:
        print("Token error:", e)
        raise credentials_exception
    return token_data

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not Validate Credentials",
                                          headers={"WWW-Authenticate": "Bearer"})

    token = verify_token_access(token, credentials_exception)

    #user = db.query(models.User).filter(models.User.id == token.id).first()

    return "user"

fake_users_db = {
    "john_doe": {
        "id": "user123",
        "userName": "john_doe",
        "password": "Secure123!",
        "type": "customer",
        "birthDate": "1990-06-15T00:00:00",
        "emailAddress": "john.doe@example.com",
        "phoneNumber": "+1-123-456-7890",
        "firstName": "John",
        "lastName": "Doe",
        "address": "123 Main St, Springfield, IL 62704"
    }
}

def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user:
        return False
    if user["password"] != password:
        return False
    return user
