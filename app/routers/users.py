from typing import Union
from fastapi import APIRouter, Depends, HTTPException
from ..helpers import auth_utils
from ..helpers import users_utils
from ..schemas.user import User
from ..logic.users import routing as user_routing_logic
import json

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

@router.put("/me")
async def update_user(payload: dict, current_user: User = Depends(auth_utils.get_current_user)):
    if current_user == None:
        raise HTTPException(status_code=404, detail="User not found")
    user_routing_logic.handleUpdateConstraints(current_user, current_user, payload)
    
    updatedUser: json = users_utils.handleUserInstanceUpdates(payload, current_user)    
    
    newUserDict = {}
    key = (current_user.id)
    newUserDict[key] = updatedUser
    auth_utils.fake_users_db.update(newUserDict)
    return updatedUser

@router.get("/{userName}", dependencies=[Depends(auth_utils.check_admin_role)])
def read_root(userName: str):
    if(auth_utils.fake_users_db.get(userName) == None):
        raise HTTPException(status_code=404, detail="User not found")
    return auth_utils.fake_users_db.get(userName)

@router.put("/{userName}")
async def update_user(userName: str, payload: dict, current_user: User = Depends(auth_utils.get_current_user)):
##apply strategy based on user role e.g.: admins can change all fields, customers only emailAddress, phoneNumber, address
#find user
    fetchedUser: User = users_utils.queryUserByUsername(userName)
#apply strategy
    user_routing_logic.handleUpdateConstraints(current_user, fetchedUser, payload)
#update user copy instance
    updatedUser: json = users_utils.handleUserInstanceUpdates(payload, fetchedUser)
#use the updated copy to overwrite db
    newUserDict = {}
    key = (fetchedUser.id)
    newUserDict[key] = updatedUser
    auth_utils.fake_users_db.update(newUserDict)
    return updatedUser

#@router.del("/{userName}")

@router.post("/")
async def create_item(user: User):
#check username exists in DB
    for dbUser in auth_utils.fake_users_db.values():
        if dbUser["userName"] == user.userName:
            raise HTTPException(status_code=404, detail="User already exists")
#create user record
    newUserDict = {}
    key = (user.id)
    newUserDict[key] = json.loads(user.model_dump_json())
    # print(newUserDict)
    auth_utils.fake_users_db.update(newUserDict)
#create primary contact record
#relate both records
    return user