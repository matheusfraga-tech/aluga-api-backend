from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
import jwt
from jwt import PyJWTError
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES"))

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
    return fake_users_db.get(token["userName"])

def check_admin_role(current_user = Depends(get_current_user)):
    print(current_user)
    if current_user["role"] != "sysAdmin":
        raise HTTPException(status_code=401, detail="Only admins")
    return current_user


def create_refresh_token(data: dict):
    to_encode = data.copy()
    print("create_refresh_token", to_encode)
    expire = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print("create_refresh_token encoded_jwt", encoded_jwt)
    return encoded_jwt

fake_users_db = {
  "john_doe": {
    "id": "b64c8392-50c1-4dbe-89c5-4a5ad3b6d06b",
    "userName": "john_doe",
    "password": "Secure123!",
    "role": "customer",
    "birthDate": "1990-06-15T00:00:00",
    "emailAddress": "john.doe@example.com",
    "phoneNumber": "+1-123-456-7890",
    "firstName": "John",
    "lastName": "Doe",
    "address": "123 Main St, Springfield, IL 62704"
  },
  "maria_lee": {
    "id": "fa51299a-bb30-4e3d-9fc3-3f64728a6b64",
    "userName": "maria_lee",
    "password": "Admin!234",
    "role": "sysAdmin",
    "birthDate": "1985-09-10T00:00:00",
    "emailAddress": "maria.lee@example.com",
    "phoneNumber": "+1-234-567-8901",
    "firstName": "Maria",
    "lastName": "Lee",
    "address": "456 Oak Ave, Chicago, IL 60616"
  },
  "james_wong": {
    "id": "9d8032e0-7638-49a2-aab0-f02b8ebee107",
    "userName": "james_wong",
    "password": "Manager#456",
    "role": "customer",
    "birthDate": "1988-03-22T00:00:00",
    "emailAddress": "james.wong@example.com",
    "phoneNumber": "+1-345-678-9012",
    "firstName": "James",
    "lastName": "Wong",
    "address": "789 Pine St, Seattle, WA 98101"
  },
  "emily_nguyen": {
    "id": "0f2bbbe3-236d-4d83-a502-12a4ad1d219d",
    "userName": "emily_nguyen",
    "password": "Employee789@",
    "role": "customer",
    "birthDate": "1992-11-05T00:00:00",
    "emailAddress": "emily.nguyen@example.com",
    "phoneNumber": "+1-456-789-0123",
    "firstName": "Emily",
    "lastName": "Nguyen",
    "address": "321 Birch Rd, Austin, TX 73301"
  },
  "oliver_smith": {
    "id": "63d7c168-77cc-4a92-8328-5cf76b79c981",
    "userName": "oliver_smith",
    "password": "Guest$321",
    "role": "customer",
    "birthDate": "1995-07-30T00:00:00",
    "emailAddress": "oliver.smith@example.com",
    "phoneNumber": "+1-567-890-1234",
    "firstName": "Oliver",
    "lastName": "Smith",
    "address": "654 Cedar Ln, Denver, CO 80202"
  }
}

def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user:
        return False
    if user["password"] != password:
        return False
    return user
