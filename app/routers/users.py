from typing import Optional
from pydantic import ValidationError
from fastapi import APIRouter, Depends, HTTPException, status
from ..helpers import auth_utils
from ..schemas.user import User, UserOut
from app.models.user import User as ORMUser
from sqlalchemy.orm import Session
from app.database.database import get_db
from ..services.user_service import UserBusinessRulesService, UserDatabaseService
from fastapi.responses import JSONResponse

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

##  ROUTES

@router.get("/", dependencies=[Depends(auth_utils.check_admin_role)])
def read_root(db: Session = Depends(get_db)):
    userList: list[User] = [UserOut.model_validate(user) for user in UserDatabaseService(db).get_all_users()]
    return userList

@router.get("/me")
def get_self(current_user: User = Depends(auth_utils.get_current_user)):
    if current_user:
        return UserOut.model_validate(current_user)
    raise HTTPException(status_code=404, detail="User not found")

@router.put("/me", response_model=User)
async def update_user(payload: dict, current_user: User = Depends(auth_utils.get_current_user), db: Session = Depends(get_db)):
    if current_user == None:
        raise HTTPException(status_code=404, detail="User not found")
    fetchedUser: ORMUser = UserDatabaseService(db).get_by_id(current_user.id)
    if not fetchedUser:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not UserBusinessRulesService.handle_update_constraints(current_user, fetchedUser, payload):
        raise HTTPException(status_code=422, detail="Unprocessable Entity")

    for key, value in payload.items():
        if hasattr(fetchedUser, key):
            setattr(fetchedUser, key, value)

    try:
        _ = User.model_validate(fetchedUser)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    
    db.commit()
    db.refresh(fetchedUser)
    response = JSONResponse(content={"message": f"User {fetchedUser.userName} updated successfully"})
    return response

@router.get("/{userName}", response_model=Optional[User], dependencies=[Depends(auth_utils.check_admin_role)])
def query_user(userName: str, db: Session = Depends(get_db)):
    return UserDatabaseService(db).get_by_username(userName)

@router.put("/{userName}", response_model=Optional[User])
async def update_user(userName: str, payload: dict, current_user: User = Depends(auth_utils.check_admin_role), db: Session = Depends(get_db)):
    fetchedUser: ORMUser = UserDatabaseService(db).get_by_username(userName)
    if not fetchedUser:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not UserBusinessRulesService.handle_update_constraints(current_user, fetchedUser, payload):
        raise HTTPException(status_code=422, detail="Unprocessable Entity")

    for key, value in payload.items():
        if hasattr(fetchedUser, key):
            setattr(fetchedUser, key, value)

    try:
        _ = User.model_validate(fetchedUser)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    
    db.commit()
    db.refresh(fetchedUser)
    response = JSONResponse(content={"message": f"User {fetchedUser.userName} updated successfully"})
    return response

@router.delete("/{userName}", dependencies=[Depends(auth_utils.check_admin_role)])
def delete_user(userName: str, db: Session = Depends(get_db)):
    fetchedUser: User = UserDatabaseService(db).get_by_username(userName)
    try:
        db.delete(fetchedUser)
        db.commit() 
    except:
        raise HTTPException(status_code=422, detail="Unprocessable Entity")
    return JSONResponse(content={"message": f"{fetchedUser.userName} deleted successfully"}, status_code=status.HTTP_200_OK)

@router.post("/", response_model=Optional[User])
async def create_user(user: User, db: Session = Depends(get_db)):
    if UserDatabaseService(db).check_exists(user.userName):
        try:
            new_user = ORMUser(**user.model_dump())
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
        except:
            raise HTTPException(status_code=422, detail="Unprocessable Entity")    
        
    response = JSONResponse(content={"message": f"User {user.userName} created successfully"})
    return response