from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base, TimeStampMixin


class Ranking(Base, TimeStampMixin):
    __tablename__ = 'rankings'

    id = Column(Integer, primary_key=True, nullable=False)
    category = Column(String, nullable=False)
    frequency = Column(String, nullable=False)


    author = relationship("Author", secondary="book_authors", back_populates="books")
    translator = relationship("Translator", secondary="book_translators", back_populates="books")
    category = relationship("Category", secondary="book_categories", back_populates="books")

