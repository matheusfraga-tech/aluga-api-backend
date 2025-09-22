
from typing import Generic, TypeVar, List
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")

class PageMeta(BaseModel):
    page: int
    size: int
    total: int

class Page(GenericModel, Generic[T]):
    meta: PageMeta
    items: List[T]

