from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base, TimeStampMixin


class Category(Base, TimeStampMixin):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey('categories.id'))


    parent = relationship("Category", back_populates="categories")
    author = relationship("Author", secondary="book_authors", back_populates="books")
    translator = relationship("Translator", secondary="book_translators", back_populates="books")
    ranking = relationship("Ranking", secondary="book_rankings", back_populates="books")

