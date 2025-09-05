from fastapi import APIRouter, HTTPException, status, Depends, Header
from ..helpers import auth_utils 
from ..schemas.login import Login
from ..schemas.token import Token
import jwt
from jwt import PyJWTError, InvalidTokenError

router = APIRouter(
    prefix="/login",
    tags=["login"]
)

    
@router.post('/')
def performLogin(login: Login):
  print(login)
  user = auth_utils.authenticate_user(login.userName, login.password)
  if not user:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid username or password")
  access_t = auth_utils.create_access_token(data={"userName": user["userName"], "role": user["role"]})
  refresh_t  = auth_utils.create_refresh_token (data={"userName": user["userName"], "role": user["role"]})
  return Token(access_token=access_t, refresh_token=refresh_t, token_role="bearer")

@router.post("/refresh")
def refresh_token(refresh_token: str = Header(None, convert_underscores=False)):
    try:
      payload = jwt.decode(refresh_token, auth_utils.SECRET_KEY, algorithms=[auth_utils.ALGORITHM])
      print("refresh", payload)
      username: str = payload.get("userName")
      if username is None:
          raise HTTPException(status_code=404, detail="User not found")
    except (PyJWTError, InvalidTokenError):
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Unathorized access, please authenticate.")
    access_t = auth_utils.create_access_token(payload)
    refresh_t = auth_utils.create_refresh_token(payload)  # Token rotation (optional but recommended)
    
    return Token(access_token=access_t, refresh_token=refresh_t, token_role="bearer")