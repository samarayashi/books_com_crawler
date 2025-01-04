from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import book as models
from ..schemas.book import BookSchema

router = APIRouter(
    prefix="/books",
    tags=["books"]
)

@router.get("/", response_model=List[BookSchema.List])
def get_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    books = db.query(models.Book).offset(skip).limit(limit).all()
    return books

@router.post("/", response_model=BookSchema.Response)
def create_book(book: BookSchema.Create, db: Session = Depends(get_db)):
    db_book = models.Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@router.get("/{book_id}", response_model=BookSchema.Response)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.patch("/{book_id}", response_model=BookSchema.Response)
def update_book(book_id: int, book: BookSchema.Update, db: Session = Depends(get_db)):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    
    for field, value in book.dict(exclude_unset=True).items():
        setattr(db_book, field, value)
    
    db.commit()
    db.refresh(db_book)
    return db_book