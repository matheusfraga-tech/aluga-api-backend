
from pydantic import BaseModel
from typing import Optional

# -------------------- SAÍDA --------------------
class MediaOut(BaseModel):
    id: int
    url: str
    kind: str

    class Config:
        from_attributes = True


# -------------------- ENTRADA --------------------
class MediaIn(BaseModel):
    url: str
    kind: Optional[str] = None  # agora opcional

    class Config:
        from_attributes = True

