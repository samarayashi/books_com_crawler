from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class BookBase(BaseModel):
    title: str
    author: str
    price: float
    isbn: str
    publisher: str
    publication_date: Optional[datetime] = None

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True 