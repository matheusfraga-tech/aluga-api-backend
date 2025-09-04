from fastapi import APIRouter, HTTPException, status, Depends, Header
from pydantic import BaseModel
from .. import dependencies
import jwt
from jwt import PyJWTError, InvalidTokenError

router = APIRouter(
    prefix="/login",
    tags=["login"]
)
class Login(BaseModel):
  userName: str
  password: str
    
@router.post('/')
def performLogin(login: Login):
  print(login)
  user = dependencies.authenticate_user(login.userName, login.password)
  if not user:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid username or password")
  access_t = dependencies.create_access_token(data={"userName": user["userName"], "type": user["type"]})
  refresh_t  = dependencies.create_refresh_token (data={"userName": user["userName"], "type": user["type"]})
  return dependencies.Token(access_token=access_t, refresh_token=refresh_t, token_type="bearer")

@router.post("/refresh")
def refresh_token(refresh_token: str = Header(None, convert_underscores=False)):
    try:
      payload = jwt.decode(refresh_token, dependencies.SECRET_KEY, algorithms=[dependencies.ALGORITHM])
      print("refresh", payload)
      username: str = payload.get("username")
      if username is None:
          print("error")
    except (PyJWTError, InvalidTokenError):
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Unathorized access, please authenticate.")
    access_t = dependencies.create_access_token(payload)
    refresh_t = dependencies.create_refresh_token(payload)  # Token rotation (optional but recommended)
    
    return dependencies.Token(access_token=access_t, refresh_token=refresh_t, token_type="bearer")