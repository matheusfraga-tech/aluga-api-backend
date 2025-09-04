from typing import Union
from fastapi import APIRouter, Depends, HTTPException
from .. import dependencies
from ..schemas.user import User

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

##  ROUTES

@router.get("/", dependencies=[Depends(dependencies.check_admin_role)])
def read_root():
    return dependencies.fake_users_db

@router.get("/me")
def get_current_user(current_user: str = Depends(dependencies.get_current_user)):
    print("outer get_current_user")
    print(current_user)
    if current_user != None:
        return current_user 
    raise HTTPException(status_code=404, detail="User not found")
#@router.put("/me")

@router.get("/{userName}", dependencies=[Depends(dependencies.check_admin_role)])
def read_root(userName: str):
    if(dependencies.fake_users_db.get(userName) == None):
        raise HTTPException(status_code=404, detail="User not found")
    return dependencies.fake_users_db.get(userName)
#@router.put("/{userName}")
#@router.del("/{userName}")

@router.post("/register")
async def create_item(user: User):
    #create user record
    #create primary contact record
    #relate both records
    return user