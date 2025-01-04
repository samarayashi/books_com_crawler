from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

# 基礎的作者信息
class AuthorBase(BaseModel):
    name: str
    ori_name: Optional[str] = None

    class Config:
        orm_mode = True

# 基礎的出版社信息
class PublisherBase(BaseModel):
    name: str

    class Config:
        orm_mode = True

# 基礎的翻譯者信息
class TranslatorBase(BaseModel):
    name: str

    class Config:
        orm_mode = True

# 基礎的分類信息
class CategoryBase(BaseModel):
    name: str

    class Config:
        orm_mode = True

class BookSchema:
    class Base(BaseModel):
        book_name: str
        ori_book_name: Optional[str] = None
        publisher_id: Optional[int] = None
        publish_date: Optional[datetime] = None
        language: Optional[str] = None
        isbn: Optional[str] = None
        blog_id: Optional[str] = None
        price: Optional[float] = None

    # 用於創建書籍的 schema
    class Create(Base):
        pass

    # 用於更新書籍的 schema
    class Update(Base):
        book_name: Optional[str] = None
        price: Optional[float] = None
        publisher_id: Optional[int] = None
        
    # 用於響應的完整書籍信息
    class Response(Base):
        id: int
        publisher: Optional[PublisherBase] = None
        authors: List[AuthorBase] = Field(default_factory=list)
        translators: List[TranslatorBase] = Field(default_factory=list)
        categories: List[CategoryBase] = Field(default_factory=list)
        created_at: datetime
        
        class Config:
            orm_mode = True

    # 用於列表顯示的簡化書籍信息
    class List(BaseModel):
        id: int
        book_name: str
        price: Optional[float]
        publisher: Optional[PublisherBase]
        
        class Config:
            orm_mode = True