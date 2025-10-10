from fastapi import HTTPException
from ...schemas.user import User

def can_current_user_update_user_record(currentUser: User, fetchedUser: User):
  return (currentUser.id == fetchedUser.id or currentUser.role == "sysAdmin")

def updateable_user_fields_by_role(currentUser: User):
  match currentUser.role:
    case "customer":
      return ["emailAddress", "phoneNumber", "address"]
    case "sysAdmin":
      return ["role", "birthDate", "emailAddress", "phoneNumber", "address"]
    case _:
      return []

def handle_update_constraints(currentUser: User, fetchedUser: User, updatePayload: dict):
  if(can_current_user_update_user_record(currentUser, fetchedUser)) != True:
    raise HTTPException(status_code=422, detail="User has no such privilege")
  
  openToUpdateFieldSet = set(updateable_user_fields_by_role(currentUser))
  payloadUpdateFieldSet = set(updatePayload.keys())
  if(payloadUpdateFieldSet.issubset(openToUpdateFieldSet)):
    return True
  else:
    diff: set = payloadUpdateFieldSet.difference(openToUpdateFieldSet)
    raise HTTPException(status_code=422, detail= f"Some fields cannot be updated with such role: {list(diff)}")
