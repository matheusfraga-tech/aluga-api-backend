from sqlalchemy.orm import Session
from app.models.user import User

class UserRepository:
  def __init__(self, db: Session):
      self.db = db

  def get_by_id(self, id: str) -> User | None:
      return self.db.query(User).filter(id == User.id).first()
  
  def get_by_username(self, username: str) -> User | None:
      return self.db.query(User).filter(username == User.userName).first()
  
  def get_all_users(self) -> User | None:
      return self.db.query(User).all()

