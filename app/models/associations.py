from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime, Table
from .base import Base


book_authors = Table(
    'book_authors',
    Base.metadata,
    Column('book_id', Integer, ForeignKey('books.id'), primary_key=True),
    Column('author_id', Integer, ForeignKey('authors.id'), primary_key=True),
)


book_translators = Table(
    'book_translators',
    Base.metadata,
    Column('book_id', Integer, ForeignKey('books.id'), primary_key=True),
    Column('translator_id', Integer, ForeignKey('translators.id'), primary_key=True),
)


book_categories = Table(
    'book_categories',
    Base.metadata,
    Column('book_id', Integer, ForeignKey('books.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True),
)


book_rankings = Table(
    'book_rankings',
    Base.metadata,
    Column('book_id', Integer, ForeignKey('books.id'), primary_key=True),
    Column('ranking_id', Integer, ForeignKey('rankings.id'), primary_key=True),
    Column('rank_date', Date, primary_key=True),
)

