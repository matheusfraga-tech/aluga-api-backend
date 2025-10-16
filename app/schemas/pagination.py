
from typing import Generic, TypeVar, List
from pydantic import BaseModel

T = TypeVar("T")

class PageMeta(BaseModel):
    page: int
    size: int
    total: int

class Page(BaseModel, Generic[T]):
    meta: PageMeta
    items: List[T]

