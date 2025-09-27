import json
from ..helpers import auth_utils
from fastapi import HTTPException, status
from ..schemas.user import User

def query_user_by_username(userName: str):
  for dbUser in auth_utils.fake_users_db.values():
    if dbUser["userName"] == userName:
      fetchedUser = User(**dbUser)
      return fetchedUser
    
  raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                          detail="User not found")

def handle_user_instance_updates(payload: dict, fetchedUser: User):
  updatedUser: json = json.loads(fetchedUser.model_dump_json())
  for toUpdateField in payload.keys():
          # print(toUpdateField, payload[toUpdateField], dbUser[toUpdateField])
          if(payload[toUpdateField] == getattr(fetchedUser, toUpdateField)):
              continue
          else: 
              print("field: ", toUpdateField, " from: ", updatedUser[toUpdateField]," to: ", payload[toUpdateField])
              updatedUser[toUpdateField] = payload[toUpdateField]
  return updatedUser