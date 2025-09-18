import json
from ..helpers import auth_utils
from ..schemas.user import User

def queryUserByUsername(userName: str):
  for dbUser in auth_utils.fake_users_db.values():
            # print(dbUser["userName"])
            if dbUser["userName"] == userName:
                fetchedUser = User(**dbUser)
                return fetchedUser

def handleUserInstanceUpdates(payload: dict, fetchedUser: User):
  updatedUser: json = json.loads(fetchedUser.model_dump_json())
  for toUpdateField in payload.keys():
          # print(toUpdateField, payload[toUpdateField], dbUser[toUpdateField])
          if(payload[toUpdateField] == getattr(fetchedUser, toUpdateField)):
              continue
          else: 
              print("field: ", toUpdateField, " from: ", updatedUser[toUpdateField]," to: ", payload[toUpdateField])
              updatedUser[toUpdateField] = payload[toUpdateField]
  return updatedUser