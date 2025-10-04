from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
import jwt
from jwt import PyJWTError
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
#from passlib.context import CryptContext
from pydantic import BaseModel
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

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
    print(to_encode["exp"])
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token_access(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        #print("ASDSADSADASD")
        print(payload)
        #user_id: str = payload.get("user_id")
        # if user_id is None:
        #     raise credentials_exception
        #refresh the token here if the remaining time is < x minutes/seconds? maybe
        token_data = payload
    except (PyJWTError, InvalidTokenError) as e:
        print("Token error:", e)
        #print("error!")
        raise credentials_exception
    return token_data

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code= 401,
                                          detail="Could not Validate Credentials",
                                          headers={"WWW-Authenticate": "Bearer"})

    token = verify_token_access(token, credentials_exception)

    #user = db.query(models.User).filter(models.User.id == token.id).first()
    #print(token)
    return token

def check_admin_role(current_user = Depends(get_current_user)):
    # Acessando a chave "type" diretamente, que é o correto
    if current_user["type"] != "sysAdmin":
        raise HTTPException(status_code=401, detail="Only admins")
    return current_user


fake_users_db = {
  "john_doe": {
    "id": "user001",
    "userName": "john_doe",
    "password": "Secure123!",
    "type": "customer",
    "birthDate": "1990-06-15T00:00:00",
    "emailAddress": "john.doe@example.com",
    "phoneNumber": "+1-123-456-7890",
    "firstName": "John",
    "lastName": "Doe",
    "address": "123 Main St, Springfield, IL 62704"
  },
  "maria_lee": {
    "id": "user002",
    "userName": "maria_lee",
    "password": "Admin!234",
    "type": "sysAdmin",
    "birthDate": "1985-09-10T00:00:00",
    "emailAddress": "maria.lee@example.com",
    "phoneNumber": "+1-234-567-8901",
    "firstName": "Maria",
    "lastName": "Lee",
    "address": "456 Oak Ave, Chicago, IL 60616"
  },
  "james_wong": {
    "id": "user003",
    "userName": "james_wong",
    "password": "Manager#456",
    "type": "customer",
    "birthDate": "1988-03-22T00:00:00",
    "emailAddress": "james.wong@example.com",
    "phoneNumber": "+1-345-678-9012",
    "firstName": "James",
    "lastName": "Wong",
    "address": "789 Pine St, Seattle, WA 98101"
  },
  "emily_nguyen": {
    "id": "user004",
    "userName": "emily_nguyen",
    "password": "Employee789@",
    "type": "customer",
    "birthDate": "1992-11-05T00:00:00",
    "emailAddress": "emily.nguyen@example.com",
    "phoneNumber": "+1-456-789-0123",
    "firstName": "Emily",
    "lastName": "Nguyen",
    "address": "321 Birch Rd, Austin, TX 73301"
  },
  "oliver_smith": {
    "id": "user005",
    "userName": "oliver_smith",
    "password": "Guest$321",
    "type": "customer",
    "birthDate": "1995-07-30T00:00:00",
    "emailAddress": "oliver.smith@example.com",
    "phoneNumber": "+1-567-890-1234",
    "firstName": "Oliver",
    "lastName": "Smith",
    "address": "654 Cedar Ln, Denver, CO 80202"
  }
}

fake_hoteis_db = {
    1: {"id": 1, "nome": "Copacabana Palace"},
    2: {"id": 2, "nome": "Hotel Fasano"}
}

fake_avaliacoes_db = [
    {
        "id": "aval001",
        "nota": 5,
        "comentario": "Estadia maravilhosa, vista incrível!",
        "hotelId": 1,
        "usuarioId": "user001"
    }
]

def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user:
        return False
    if user["password"] != password:
        return False
    return user
