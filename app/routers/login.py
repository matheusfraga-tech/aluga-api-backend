from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from .. import dependencies

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
  access_token = dependencies.create_access_token(data={"user_id": user["id"]})
  return {"access_token": access_token, "token_type": "bearer"}
  return (login)