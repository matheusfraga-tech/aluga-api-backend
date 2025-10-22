from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..schemas.user import User
from ..repositories.user_repository import UserRepository

class UserDatabaseService:
  def __init__(self, db: Session):
        self.repo = UserRepository(db)
  
  def get_by_id(self, id: str):
    userORM = self.repo.get_by_id(id)
    if not userORM:
      raise HTTPException(status_code=404, detail="User not found")
    return userORM
  
  def get_by_username(self, username: str):
    userORM = self.repo.get_by_username(username)
    if not userORM:
      raise HTTPException(status_code=404, detail="User not found")
    return userORM
  
  def check_exists(self, username: str):
    userORM = self.repo.get_by_username(username)
    if not userORM:
      return True
    raise HTTPException(status_code=422, detail="User already exists")
  
  def get_all_users(self):
    userList = self.repo.get_all_users()
    if not userList:
      raise HTTPException(status_code=404, detail="User not found")
    return userList
  
class UserBusinessRulesService:
  
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
    if(UserBusinessRulesService.can_current_user_update_user_record(currentUser, fetchedUser)) != True:
      raise HTTPException(status_code=422, detail="User has no such privilege")
    
    openToUpdateFieldSet = set(UserBusinessRulesService.updateable_user_fields_by_role(currentUser))
    payloadUpdateFieldSet = set(updatePayload.keys())
    if(payloadUpdateFieldSet.issubset(openToUpdateFieldSet)):
      return True
    else:
      diff: set = payloadUpdateFieldSet.difference(openToUpdateFieldSet)
      raise HTTPException(status_code=422, detail= f"Some fields cannot be updated with such role: {list(diff)}")