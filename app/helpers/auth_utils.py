from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
import jwt
from jwt import PyJWTError
from fastapi import Depends, HTTPException, status, Cookie, Request
from jwt.exceptions import InvalidTokenError
from ..schemas.user import User
from ..schemas.token import TokenData, Token
from ..schemas.login import Login
from fastapi.responses import JSONResponse


load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES"))

def authenticate_user(login: Login):
  # no iteration needed on a real db so its an O(1) statement
  # passwords are still to be hashed
  for user in fake_users_db.values():
      if user["userName"] == login.userName:
          if user["password"] == login.password:
              return user
          raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                          detail="Invalid username or password")
  raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                          detail="Invalid username or password")

def perform_login(login: Login):
    user = authenticate_user(login)
    
    access_t = create_access_token(TokenData(id=user["id"], role=user["role"]))
    refresh_t  = create_refresh_token (TokenData(id=user["id"], role=user["role"])) 
    tokenContent = Token(access_token=access_t, refresh_token=refresh_t, token_role="bearer")
    
    response = JSONResponse(content={"message": "Login successful", "token_content": tokenContent.model_dump()})
    response.set_cookie(
            key="access_token",
            value=access_t,
            httponly=False,  # Secure against XSS
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="lax",  # Adjust for cross-site if needed
            secure=False,     # True in production (HTTPS)
            path="/"
        )
    response.set_cookie(
            key="refresh_token",
            value=refresh_t,
            httponly=False,  # Secure against XSS
            max_age=REFRESH_TOKEN_EXPIRE_MINUTES * 60,
            samesite="lax",  # Adjust for cross-site if needed
            secure=False,     # True in production (HTTPS)
            path="/"
        )
    return response;

def perform_refresh(request: Request):
    refresh_token = handle_auth_method(request, "refresh_token");
    try:
      payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
      user: str = payload
      
      if user["id"] is None:
        raise HTTPException(status_code=404, detail="User not found")
    except (PyJWTError, InvalidTokenError):
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Unauthorized access, please authenticate.")
    access_t = create_access_token(TokenData(id=user["id"], role=user["role"]))
    refresh_t = create_refresh_token(TokenData(id=user["id"], role=user["role"]))
    tokenContent = Token(access_token=access_t, refresh_token=refresh_t, token_role="bearer")

    response = JSONResponse(content={"message": "Token refreshed successfully", "token_content": tokenContent.model_dump()})
    response.set_cookie(
            key="access_token",
            value=access_t,
            httponly=False,  # Secure against XSS
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="lax",  # Adjust for cross-site if needed
            secure=False,     # True in production (HTTPS)
            path="/"
        )
    response.set_cookie(
            key="refresh_token",
            value=refresh_t,
            httponly=False,  # Secure against XSS
            max_age=REFRESH_TOKEN_EXPIRE_MINUTES * 60,
            samesite="lax",  # Adjust for cross-site if needed
            secure=False,     # True in production (HTTPS)
            path="/"
        )
    return response;

def create_access_token(data: TokenData):
    to_encode = data.model_dump()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})  # this will be properly interpreted by JWT
    print(to_encode["exp"])
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token_access(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        #print("ASDSADSADASD")
        #print(payload)
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

async def get_current_user(request: Request):
    access_token = handle_auth_method(request, "refresh_token");
    
    credentials_exception = HTTPException(status_code= 401,
                                          detail="Could not Validate Credentials",
                                          headers={"WWW-Authenticate": "Bearer"})

    token = access_token # or bearer_token
    if not token:
      raise credentials_exception
    token_data = verify_token_access(token, credentials_exception)
    user_data = fake_users_db.get(token_data["id"])
    if not user_data:
        raise credentials_exception
    
    #must query db
    return User(**user_data)

def check_admin_role(current_user = Depends(get_current_user)):
    if current_user.role != "sysAdmin":
        raise HTTPException(status_code=401, detail="Only admins")
    return current_user 

def create_refresh_token(data: TokenData):
    to_encode = data.model_dump()
    print("create_refresh_token", to_encode)
    expire = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print("create_refresh_token encoded_jwt", encoded_jwt)
    return encoded_jwt

def handle_auth_method(request: Request, key: str):
  keyValue: str = None;
  if request.headers.get(key) != None:
      keyValue = request.headers.get(key)
      print("header token auth")
  elif request.cookies.get(key) != None:
      keyValue = request.cookies.get(key)
      print("cookie auth")
  if not keyValue:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                      detail="Unauthorized access, please authenticate.")
  return keyValue

fake_users_db = {
  "b64c8392-50c1-4dbe-89c5-4a5ad3b6d06b": {
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
  "fa51299a-bb30-4e3d-9fc3-3f64728a6b64": {
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
  "9d8032e0-7638-49a2-aab0-f02b8ebee107": {
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
  "0f2bbbe3-236d-4d83-a502-12a4ad1d219d": {
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
  "63d7c168-77cc-4a92-8328-5cf76b79c981": {
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
