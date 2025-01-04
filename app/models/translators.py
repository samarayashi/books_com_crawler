from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base, TimeStampMixin


class Translator(Base, TimeStampMixin):
    __tablename__ = 'translators'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)


    author = relationship("Author", secondary="book_authors", back_populates="books")
    category = relationship("Category", secondary="book_categories", back_populates="books")
    ranking = relationship("Ranking", secondary="book_rankings", back_populates="books")

