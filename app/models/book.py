from sqlalchemy import Column, Integer, String, Float, DateTime
from ..database import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    price = Column(Float)
    isbn = Column(String, unique=True, index=True)
    publisher = Column(String)
    publication_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default='now()')