from pydantic  import BaseModel

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_role: str

class TokenData(BaseModel):
    id: str
    role: str
    userName:str