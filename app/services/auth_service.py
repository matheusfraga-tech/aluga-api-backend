from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
import jwt
from jwt import PyJWTError
from fastapi import Depends, HTTPException, status, Cookie, Request
from jwt.exceptions import InvalidTokenError
from ..schemas.token import TokenData, Token
from ..schemas.login import Login
from fastapi.responses import JSONResponse
from app.database.database import get_db
from ..services.user_service import UserDatabaseService


load_dotenv()
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
REFRESH_TOKEN_SECRET = os.getenv("REFRESH_TOKEN_SECRET")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES"))

async def get_current_user(request: Request):
    
    access_token = handle_auth_method(request, "access_token");
    print(access_token)
    credentials_exception = HTTPException(status_code= 401,
                                          detail="Could not Validate Credentials",
                                          headers={"WWW-Authenticate": "Bearer"})
    
    if not access_token:
      raise credentials_exception
    access_token_data = verify_token_access(access_token, credentials_exception)
    db_gen = get_db()
    db = next(db_gen)   
    user_data = UserDatabaseService(db).get_by_id(access_token_data["id"])
    db_gen.close()
    if not user_data:
        raise credentials_exception
    
    #must query db
    return user_data

def check_admin_role(current_user = Depends(get_current_user)):
    if current_user.role != "sysAdmin":
        raise HTTPException(status_code=401, detail="Only admins")
    return current_user 

def authenticate_user(login: Login):
  # passwords are still to be hashed
  db_gen = get_db()
  db = next(db_gen)
  
  fetchedUser = UserDatabaseService(db).get_by_username(login.userName)
  if not fetchedUser:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
  db_gen.close()

  if(login.userName == fetchedUser.userName and login.password == fetchedUser.password):
     return fetchedUser
  raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

def get_credentials(request):
    access_token = handle_auth_method(request, "access_token");
    
    try:
      payload = jwt.decode(access_token, ACCESS_TOKEN_SECRET, algorithms=[ALGORITHM])
    except (PyJWTError, InvalidTokenError):
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Unauthorized access, please authenticate.")
    
    response = JSONResponse(content={"token_content": payload})
    return response

def perform_login(login: Login):
    user = authenticate_user(login)

    access_t = create_access_token(TokenData(id=user.id, role=user.role))
    refresh_t  = create_refresh_token (TokenData(id=user.id, role=user.role)) 
    tokenContent = Token(access_token=access_t, refresh_token=refresh_t, token_role="bearer")
    
    response = JSONResponse(content={"message": "Login successful", "token_content": tokenContent.model_dump()})
    response.set_cookie(
            key="access_token",
            value=access_t,
            httponly=True,  # Secure against XSS
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="None",  # Adjust for cross-site if needed
            secure=True,     # True in production (HTTPS)
            path="/"
        )
    response.set_cookie(
            key="refresh_token",
            value=refresh_t,
            httponly=True,  # Secure against XSS
            max_age=REFRESH_TOKEN_EXPIRE_MINUTES * 60,
            samesite="None",  # Adjust for cross-site if needed
            secure=True,     # True in production (HTTPS)
            path="/"
        )
    return response;

def perform_logout(request: Request, current_user = Depends(get_current_user)):

  response = JSONResponse(content={"message": "Logout successfully"})
  # Cookies are working
  
  response.delete_cookie(
        key="access_token",
        httponly=True,  # Secure against XSS
        samesite="None",  # Adjust for cross-site if needed
        secure=True,     # True in production (HTTPS)
        path="/"
        )
  response.delete_cookie(
        key="refresh_token",
        httponly=True,  # Secure against XSS
        samesite="None",  # Adjust for cross-site if needed
        secure=True,     # True in production (HTTPS)
        path="/"
        )

  # For headers
  print("HEADERS: ")
  print(request.headers.keys())
  print("COOKIES: ")
  print(request.cookies.keys())
    # Invalidate access and refresh token
    # Needs db working
  return response

def perform_refresh(request: Request):
    refresh_token = handle_auth_method(request, "refresh_token");
    try:
      payload = jwt.decode(refresh_token, REFRESH_TOKEN_SECRET, algorithms=[ALGORITHM])
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
            httponly=True,  # Secure against XSS
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="None",  # Adjust for cross-site if needed
            secure=True,     # True in production (HTTPS)
            path="/"
        )
    response.set_cookie(
            key="refresh_token",
            value=refresh_t,
            httponly=True,  # Secure against XSS
            max_age=REFRESH_TOKEN_EXPIRE_MINUTES * 60,
            samesite="None",  # Adjust for cross-site if needed
            secure=True,     # True in production (HTTPS)
            path="/"
        )
    return response;

def create_access_token(data: TokenData):
    to_encode = data.model_dump()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})  # this will be properly interpreted by JWT
    print(to_encode["exp"])
    encoded_jwt = jwt.encode(to_encode, ACCESS_TOKEN_SECRET, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token_access(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, ACCESS_TOKEN_SECRET, algorithms=[ALGORITHM])
        token_data = payload
    except (PyJWTError, InvalidTokenError) as e:
        print(token)
        print("Token error:", e)
        raise credentials_exception
    return token_data

def create_refresh_token(data: TokenData):
    to_encode = data.model_dump()
    print("create_refresh_token", to_encode)
    expire = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, REFRESH_TOKEN_SECRET, algorithm=ALGORITHM)
    print("create_refresh_token encoded_jwt", encoded_jwt)
    return encoded_jwt

def handle_auth_method(request: Request, key: str):
  print(request.cookies)
  print(request.headers)
  keyValue: str = None;
  if request.headers.get(key) != None:
      keyValue = request.headers.get(key)
      print("header token auth")
  elif request.cookies.get(key) != None:
      keyValue = request.cookies.get(key)
      print("cookie auth", keyValue)
  if not keyValue:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                      detail="No authentication data found, please authenticate")
  return keyValue