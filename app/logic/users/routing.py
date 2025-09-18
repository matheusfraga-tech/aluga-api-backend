from fastapi import HTTPException
from ...schemas.user import User

def canCurrentUserUpdateUserRecord(currentUser: User, fetchedUser: User):
  print(type(currentUser))
  return (currentUser.id == fetchedUser.id or currentUser.role == "sysAdmin")

def updateableUserFieldsByRole(currentUser: User):
  match currentUser.role:
    case "customer":
      return ["emailAddress", "phoneNumber", "address"]
    case "sysAdmin":
      return ["role", "birthDate", "emailAddress", "phoneNumber", "address"]
    case _:
      return []

def handleUpdateConstraints(currentUser: User, fetchedUser: User, updatePayload: dict):
  if(canCurrentUserUpdateUserRecord(currentUser, fetchedUser)) != True:
    raise HTTPException(status_code=422, detail="User has no such privilege")
  
  openToUpdateFieldSet = set(updateableUserFieldsByRole(currentUser))
  payloadUpdateFieldSet = set(updatePayload.keys())
  if(payloadUpdateFieldSet.issubset(openToUpdateFieldSet)):
    return True
  else:
    diff: set = payloadUpdateFieldSet.difference(openToUpdateFieldSet)
    raise HTTPException(status_code=422, detail= f"Some fields cannot be updated with such role: {list(diff)}")
