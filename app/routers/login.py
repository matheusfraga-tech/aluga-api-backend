from fastapi import APIRouter, Request
from ..helpers import auth_utils 
from ..schemas.login import Login
import json

router = APIRouter(
    tags=["login"]
)

responses_login: json = {
  200: {
    "content": {
      "application/json": {
        "example": {
          "message": "Login successful",
          "token_content": {
            "access_token": "[access_token value]",
            "refresh_token": "[access_token value]",
            "token_role": "bearer"
          }
        }
      }
    }
  }
}

responses_refresh: json = {
  200: {
    "content": {
      "application/json": {
        "example": {
          "message": "Token refreshed successfully",
          "token_content": {
            "access_token": "[access_token value]",
            "refresh_token": "[access_token value]",
            "token_role": "bearer"
          }
        }
      }
    }
  }
}

@router.post('/login', responses=responses_login)
def perform_login(login: Login):
  return auth_utils.perform_login(login)

@router.post("/logout", responses=responses_refresh)
def perform_logout(request: Request):
  return auth_utils.perform_logout(request)

@router.post("/refresh", responses=responses_refresh)
def refresh_token(request: Request):
  return auth_utils.perform_refresh(request)