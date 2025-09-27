from pydantic  import BaseModel

class Login(BaseModel):
  userName: str
  password: str