from typing import Union
from fastapi import APIRouter, Depends, HTTPException
from ..helpers import auth_utils
from ..schemas.user import User

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

##  ROUTES

@router.get("/", dependencies=[Depends(auth_utils.check_admin_role)])
def read_root():
    return auth_utils.fake_users_db

@router.get("/me")
def get_self(current_user: str = Depends(auth_utils.get_current_user)):
    if current_user != None:
        return current_user
    raise HTTPException(status_code=404, detail="User not found")
#@router.put("/me")

@router.get("/{userName}", dependencies=[Depends(auth_utils.check_admin_role)])
def read_root(userName: str):
    if(auth_utils.fake_users_db.get(userName) == None):
        raise HTTPException(status_code=404, detail="User not found")
    return auth_utils.fake_users_db.get(userName)
#@router.put("/{userName}")
#@router.del("/{userName}")

@router.post("/register")
async def create_item(user: User):
    #create user record
    #create primary contact record
    #relate both records
    return user