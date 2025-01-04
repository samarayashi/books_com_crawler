from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base, TimeStampMixin


class Book(Base, TimeStampMixin):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, nullable=False)
    book_name = Column(String, nullable=False)
    ori_book_name = Column(String)
    publisher_id = Column(Integer, ForeignKey('publishers.id'))
    publish_date = Column(Date)
    language = Column(String)
    isbn = Column(String)
    blog_id = Column(String)
    price = Column(Float)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


    publisher = relationship("Publisher", back_populates="books")
    author = relationship("Author", secondary="book_authors", back_populates="books")
    translator = relationship("Translator", secondary="book_translators", back_populates="books")
    category = relationship("Category", secondary="book_categories", back_populates="books")
    ranking = relationship("Ranking", secondary="book_rankings", back_populates="books")

