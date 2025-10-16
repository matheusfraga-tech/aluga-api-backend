from pydantic import BaseModel

# --- SAÍDA (response) ---
class AmenityOut(BaseModel):
    id: int
    code: str
    label: str

    class Config:
        from_attributes = True

# --- ENTRADA (input) ---
class AmenityIn(BaseModel):
    id: int  # apenas o ID do amenity para associação

    class Config:
        from_attributes = True

