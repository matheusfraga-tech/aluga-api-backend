from fastapi import APIRouter, Cookie
from typing import Optional
from ..helpers import auth_utils 
from ..schemas.login import Login

router = APIRouter(
    prefix="/login",
    tags=["login"]
)

@router.post('/')
def performLogin(login: Login):
  return auth_utils.perform_login(login)

@router.post("/refresh")
def refresh_token(refresh_token: Optional[str] = Cookie(None)):
  return auth_utils.perform_refresh(refresh_token)