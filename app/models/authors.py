from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base, TimeStampMixin


class Author(Base, TimeStampMixin):
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    ori_name = Column(String)


    translator = relationship("Translator", secondary="book_translators", back_populates="books")
    category = relationship("Category", secondary="book_categories", back_populates="books")
    ranking = relationship("Ranking", secondary="book_rankings", back_populates="books")

